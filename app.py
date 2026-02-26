from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps
import secrets

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))

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
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
APPROVAL_REQUIRED = os.getenv('APPROVAL_REQUIRED', 'false').lower() == 'true'
PENDING_IMAGE_EXPIRY_MINUTES = int(os.getenv('PENDING_IMAGE_EXPIRY_MINUTES', '30'))

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
            enabled INTEGER DEFAULT 1,
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
    db.execute('''
        CREATE TABLE IF NOT EXISTS pending_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
        )
    ''')
    
    # Add enabled column if it doesn't exist (migration)
    try:
        db.execute('ALTER TABLE rooms ADD COLUMN enabled INTEGER DEFAULT 1')
    except:
        pass
    
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
        
        # Clean up expired pending images
        pending_cutoff = datetime.now() - timedelta(minutes=PENDING_IMAGE_EXPIRY_MINUTES)
        pending_images = db.execute(
            'SELECT image_path FROM pending_images WHERE uploaded_at < ? AND status = ?',
            (pending_cutoff, 'pending')
        ).fetchall()
        
        for img in pending_images:
            filepath = img['image_path']
            if os.path.exists(filepath):
                os.remove(filepath)
        
        db.execute('DELETE FROM pending_images WHERE uploaded_at < ? AND status = ?', 
                   (pending_cutoff, 'pending'))
        
        db.commit()
        db.close()

        print(f"[AUTO-PURGE] Deleted {len(old_images)} images older than {AUTO_PURGE_HOURS}h and {len(pending_images)} expired pending images")
    except Exception as e:
        print(f"[AUTO-PURGE ERROR] {str(e)}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=purge_old_images, trigger="interval", hours=1)
    scheduler.start()
    print(f"[SCHEDULER] Auto-purge enabled: every 1 hour (deletes images older than {AUTO_PURGE_HOURS}h)")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    return render_template('login.html', server_url=SERVER_URL)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('admin.html', server_url=SERVER_URL, approval_required=APPROVAL_REQUIRED)
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', server_url=SERVER_URL, approval_required=APPROVAL_REQUIRED)

@app.route('/display/<room_id>')
def display(room_id):
    return render_template('display.html', room_id=room_id, server_url=SERVER_URL, slide_duration=SLIDE_DURATION)

@app.route('/upload/<room_id>')
def upload(room_id):
    return render_template('upload.html', room_id=room_id, server_url=SERVER_URL)

@app.route('/api/rooms', methods=['GET'])
@login_required
def get_rooms():
    db = get_db()
    rooms = db.execute('SELECT * FROM rooms ORDER BY created_at DESC').fetchall()
    db.close()
    return jsonify([dict(room) for room in rooms])

@app.route('/api/rooms', methods=['POST'])
@login_required
def create_room():
    data = request.json
    room_name = data.get('name')

    if not room_name:
        return jsonify({'success': False, 'error': 'Room name required'}), 400

    room_id = str(uuid.uuid4())[:8]

    db = get_db()
    db.execute('INSERT INTO rooms (id, name, enabled) VALUES (?, ?, ?)', (room_id, room_name, 1))
    db.commit()
    db.close()

    return jsonify({'success': True, 'room_id': room_id, 'name': room_name})

@app.route('/api/rooms/<room_id>/toggle', methods=['POST'])
@login_required
def toggle_room(room_id):
    db = get_db()
    room = db.execute('SELECT enabled FROM rooms WHERE id = ?', (room_id,)).fetchone()
    
    if not room:
        db.close()
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    new_enabled = 1 - room['enabled']
    db.execute('UPDATE rooms SET enabled = ? WHERE id = ?', (new_enabled, room_id))
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'enabled': new_enabled})

@app.route('/api/rooms/<room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    db = get_db()

    images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()
    pending = db.execute('SELECT image_path FROM pending_images WHERE room_id = ?', (room_id,)).fetchall()

    for img in images:
        filepath = img['image_path']
        if os.path.exists(filepath):
            os.remove(filepath)
    
    for img in pending:
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
    
    # Check if room exists
    room = db.execute('SELECT enabled FROM rooms WHERE id = ?', (room_id,)).fetchone()
    if not room:
        db.close()
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    # If room is disabled, still save but as pending (so user sees QR is working)
    if not room['enabled']:
        return jsonify({'success': False, 'error': 'Room is disabled'}), 403

    saved_count = 0
    
    if APPROVAL_REQUIRED:
        # Save to pending_images table
        for file in files:
            if file and file.filename:
                unique_filename = f"{room_id}_{uuid.uuid4().hex[:8]}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                db.execute('INSERT INTO pending_images (room_id, image_path, status) VALUES (?, ?, ?)', 
                          (room_id, filepath, 'pending'))
                saved_count += 1
        db.commit()
    else:
        # Original behavior: replace all images
        existing_images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()
        for img in existing_images:
            filepath = img['image_path']
            if os.path.exists(filepath):
                os.remove(filepath)

        db.execute('DELETE FROM room_images WHERE room_id = ?', (room_id,))

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
    
    # Check if room is enabled
    room = db.execute('SELECT enabled FROM rooms WHERE id = ?', (room_id,)).fetchone()
    if room and not room['enabled']:
        db.close()
        return jsonify({'images': [], 'disabled': True})
    
    images = db.execute(
        'SELECT image_path FROM room_images WHERE room_id = ? ORDER BY uploaded_at ASC',
        (room_id,)
    ).fetchall()
    db.close()

    image_urls = [f"{SERVER_URL}/{img['image_path']}" for img in images]

    return jsonify({'images': image_urls, 'disabled': False})

@app.route('/api/pending_images/<room_id>', methods=['GET'])
@login_required
def get_pending_images(room_id):
    db = get_db()
    pending = db.execute(
        'SELECT id, image_path, uploaded_at FROM pending_images WHERE room_id = ? AND status = ? ORDER BY uploaded_at DESC',
        (room_id, 'pending')
    ).fetchall()
    db.close()
    
    result = []
    for img in pending:
        result.append({
            'id': img['id'],
            'url': f"{SERVER_URL}/{img['image_path']}",
            'uploaded_at': img['uploaded_at']
        })
    
    return jsonify({'pending': result})

@app.route('/api/pending_images/<int:pending_id>/approve', methods=['POST'])
@login_required
def approve_image(pending_id):
    db = get_db()
    pending = db.execute('SELECT room_id, image_path FROM pending_images WHERE id = ?', (pending_id,)).fetchone()
    
    if not pending:
        db.close()
        return jsonify({'success': False, 'error': 'Image not found'}), 404
    
    room_id = pending['room_id']
    image_path = pending['image_path']
    
    # Add approved image to room (don't delete existing ones - add to slideshow)
    db.execute('INSERT INTO room_images (room_id, image_path) VALUES (?, ?)', (room_id, image_path))
    db.execute('UPDATE pending_images SET status = ? WHERE id = ?', ('approved', pending_id))
    
    db.commit()
    db.close()
    
    return jsonify({'success': True})

@app.route('/api/pending_images/<int:pending_id>/deny', methods=['POST'])
@login_required
def deny_image(pending_id):
    db = get_db()
    pending = db.execute('SELECT image_path FROM pending_images WHERE id = ?', (pending_id,)).fetchone()
    
    if not pending:
        db.close()
        return jsonify({'success': False, 'error': 'Image not found'}), 404
    
    image_path = pending['image_path']
    if os.path.exists(image_path):
        os.remove(image_path)
    
    db.execute('DELETE FROM pending_images WHERE id = ?', (pending_id,))
    db.commit()
    db.close()
    
    return jsonify({'success': True})

@app.route('/api/clear_images/<room_id>', methods=['POST'])
@login_required
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
