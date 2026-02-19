from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
# Persist SQLite DB inside the container under /app/data/qr_rooms.db (mounted to host ./data)
DATA_FOLDER = 'data'
DATABASE = os.path.join(DATA_FOLDER, 'qr_rooms.db')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

SERVER_IP = os.getenv('SERVER_IP', '10.192.128.125')
SERVER_PORT = os.getenv('SERVER_PORT', '5000')
SERVER_URL = f'http://{SERVER_IP}:{SERVER_PORT}'
AUTO_PURGE_ENABLED = os.getenv('AUTO_PURGE_ENABLED', 'true').lower() == 'true'
AUTO_PURGE_HOURS = int(os.getenv('AUTO_PURGE_HOURS', '48'))
SLIDE_DURATION = int(os.getenv('SLIDE_DURATION', '10000'))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS room_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
        )
    ''')
    db.commit()
    db.close()

def purge_old_images():
    if not AUTO_PURGE_ENABLED:
        return

    try:
        db = get_db()
        cutoff_time = datetime.now() - timedelta(hours=AUTO_PURGE_HOURS)

        old_images = db.execute(
            'SELECT image_path FROM room_images WHERE uploaded_at < ?',
            (cutoff_time,)
        ).fetchall()

        for img in old_images:
            filepath = img['image_path']
            if os.path.exists(filepath):
                os.remove(filepath)

        db.execute('DELETE FROM room_images WHERE uploaded_at < ?', (cutoff_time,))
        db.commit()
        db.close()

        print(f"[AUTO-PURGE] Deleted {len(old_images)} images older than {AUTO_PURGE_HOURS} hours")
    except Exception as e:
        print(f"[AUTO-PURGE ERROR] {str(e)}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=purge_old_images, trigger="interval", hours=1)
    scheduler.start()
    print(f"[SCHEDULER] Auto-purge enabled: every 1 hour (deletes images older than {AUTO_PURGE_HOURS}h)")

@app.route('/')
def index():
    return render_template('admin.html', server_url=SERVER_URL)

@app.route('/admin')
def admin():
    return render_template('admin.html', server_url=SERVER_URL)

@app.route('/display/<room_id>')
def display(room_id):
    return render_template('display.html', room_id=room_id, server_url=SERVER_URL, slide_duration=SLIDE_DURATION)

@app.route('/upload/<room_id>')
def upload(room_id):
    return render_template('upload.html', room_id=room_id, server_url=SERVER_URL)

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    db = get_db()
    rooms = db.execute('SELECT * FROM rooms ORDER BY created_at DESC').fetchall()
    db.close()
    return jsonify([dict(room) for room in rooms])

@app.route('/api/rooms', methods=['POST'])
def create_room():
    data = request.json
    room_name = data.get('name')

    if not room_name:
        return jsonify({'success': False, 'error': 'Room name required'}), 400

    room_id = str(uuid.uuid4())[:8]

    db = get_db()
    db.execute('INSERT INTO rooms (id, name) VALUES (?, ?)', (room_id, room_name))
    db.commit()
    db.close()

    return jsonify({'success': True, 'room_id': room_id, 'name': room_name})

@app.route('/api/rooms/<room_id>', methods=['DELETE'])
def delete_room(room_id):
    db = get_db()

    images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()

    for img in images:
        filepath = img['image_path']
        if os.path.exists(filepath):
            os.remove(filepath)

    db.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
    db.commit()
    db.close()

    return jsonify({'success': True})

@app.route('/api/save_images/<room_id>', methods=['POST'])
def save_images(room_id):
    if 'images[]' not in request.files:
        return jsonify({'success': False, 'error': 'No images provided'}), 400

    files = request.files.getlist('images[]')

    if not files:
        return jsonify({'success': False, 'error': 'No images provided'}), 400

    db = get_db()

    existing_images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()
    for img in existing_images:
        filepath = img['image_path']
        if os.path.exists(filepath):
            os.remove(filepath)

    db.execute('DELETE FROM room_images WHERE room_id = ?', (room_id,))

    saved_count = 0
    for file in files:
        if file and file.filename:
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{room_id}_{uuid.uuid4().hex[:8]}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            file.save(filepath)

            db.execute('INSERT INTO room_images (room_id, image_path) VALUES (?, ?)', (room_id, filepath))
            saved_count += 1

    db.commit()
    db.close()

    return jsonify({'success': True, 'count': saved_count})

@app.route('/api/get_images/<room_id>', methods=['GET'])
def get_images(room_id):
    db = get_db()
    images = db.execute(
        'SELECT image_path FROM room_images WHERE room_id = ? ORDER BY uploaded_at ASC',
        (room_id,)
    ).fetchall()
    db.close()

    image_urls = [f"{SERVER_URL}/{img['image_path']}" for img in images]

    return jsonify({'images': image_urls})

@app.route('/api/clear_images/<room_id>', methods=['POST'])
def clear_images(room_id):
    db = get_db()

    images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()

    for img in images:
        filepath = img['image_path']
        if os.path.exists(filepath):
            os.remove(filepath)

    db.execute('DELETE FROM room_images WHERE room_id = ?', (room_id,))
    db.commit()
    db.close()

    return jsonify({'success': True})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    if AUTO_PURGE_ENABLED:
        start_scheduler()
    app.run(host='0.0.0.0', port=5000, debug=False)
