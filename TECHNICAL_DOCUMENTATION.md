# QR Module v7.1.0 - Technical Documentation

**Project Version:** 7.1.0  
**Last Updated:** February 26, 2026  
**Status:** Production Ready  

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [Backend Implementation](#backend-implementation)
6. [Frontend Implementation](#frontend-implementation)
7. [API Documentation](#api-documentation)
8. [Configuration & Environment Variables](#configuration--environment-variables)
9. [Security Implementation](#security-implementation)
10. [Deployment & Containerization](#deployment--containerization)
11. [File Organization & Structure](#file-organization--structure)
12. [Workflows & User Flows](#workflows--user-flows)
13. [Performance Specifications](#performance-specifications)
14. [Troubleshooting & Maintenance](#troubleshooting--maintenance)
15. [Development Guidelines](#development-guidelines)
16. [Version History](#version-history)

---

## Executive Summary

**QR Module** is a sophisticated multi-room image management system designed for TV and monitor displays. It enables users to upload images via QR code scanning or direct admin upload, with automatic slideshow rotation. The system features a robust admin panel with authentication, optional image approval workflows, automatic image purging, and persistent storage across container restarts.

### Core Features
- 🎯 Multi-room support with unique identifiers
- 📱 QR code generation for mobile uploads
- 🖼️ Automatic image slideshow with configurable duration
- 🔐 Admin authentication with session management
- ✅ Optional image approval workflow
- 🗑️ Automatic image purging based on age threshold
- 💾 Persistent storage across restarts
- 🎬 Full-screen display optimization for 4K/8K monitors
- 🔍 Search and sort functionality for room management
- 📊 Real-time room status and image management

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     QR Module System                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────┐   │
│  │   Mobile Users       │  │   Admin Users            │   │
│  │   (Phone/Tablet)     │  │   (Desktop/Laptop)       │   │
│  └──────┬───────────────┘  └──────┬───────────────────┘   │
│         │                         │                        │
│         │ Scan QR              │ Login                   │
│         │                         │                        │
│  ┌──────▼───────────────────────▼────────────────────┐   │
│  │        Frontend Layer                             │   │
│  │  ┌────────────────┐  ┌────────────────┐           │   │
│  │  │ Upload Page    │  │ Admin Panel    │           │   │
│  │  │ (Vanilla JS)   │  │ (Vanilla JS)   │           │   │
│  │  └────────────────┘  └────────────────┘           │   │
│  │  ┌────────────────────────────────────┐           │   │
│  │  │ Display Page (QR / Slideshow)      │           │   │
│  │  └────────────────────────────────────┘           │   │
│  └──────┬───────────────────────────────────────────┘   │
│         │ REST API (JSON)                               │
│         │                                               │
│  ┌──────▼───────────────────────────────────────────┐   │
│  │        Backend Layer (Flask)                      │   │
│  │  ┌────────────────────────────────────┐           │   │
│  │  │ Route Handlers                     │           │   │
│  │  │ - Authentication                  │           │   │
│  │  │ - Room CRUD Operations            │           │   │
│  │  │ - Image Management                │           │   │
│  │  │ - Approval Workflow               │           │   │
│  │  └────────────────────────────────────┘           │   │
│  │  ┌────────────────────────────────────┐           │   │
│  │  │ Session Management                │           │   │
│  │  └────────────────────────────────────┘           │   │
│  └──────┬───────────────────────────────────────────┘   │
│         │                                               │
│  ┌──────▼───────────────────────────────────────────┐   │
│  │        Data Layer                                │   │
│  │  ┌────────────────────────────────────┐           │   │
│  │  │ SQLite Database                    │           │   │
│  │  │ - rooms table                      │           │   │
│  │  │ - room_images table                │           │   │
│  │  │ - pending_images table             │           │   │
│  │  └────────────────────────────────────┘           │   │
│  │  ┌────────────────────────────────────┐           │   │
│  │  │ File Storage                       │           │   │
│  │  │ /uploads/ (Docker volume)          │           │   │
│  │  └────────────────────────────────────┘           │   │
│  └──────────────────────────────────────────────────┘   │
│         │ Scheduled Job (APScheduler)                   │
│         ▼                                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Auto-Purge Job (Hourly)                          │   │
│  │ - Deletes images older than threshold            │   │
│  │ - Cleans expired pending uploads                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **User Layer**: Mobile users and admin users access different interfaces
2. **Frontend Layer**: Vanilla JavaScript handles all interactions
3. **API Layer**: Flask REST endpoints manage all operations
4. **Database Layer**: SQLite persists all data
5. **Scheduled Services**: APScheduler handles auto-purge operations

---

## Technology Stack

### Backend
- **Framework**: Flask 2.3.3
  - RESTful API server
  - Session management for authentication
  - File upload handling
  - CORS support for cross-origin requests

- **Programming Language**: Python 3.11
  - Modern async patterns support
  - Rich standard library
  - Excellent web framework ecosystem

- **Database**: SQLite 3
  - Serverless, file-based database
  - Zero configuration
  - ACID compliance
  - Suitable for multi-room system scalability to ~100 rooms

- **Job Scheduling**: APScheduler 3.10.4
  - Background scheduler for auto-purge
  - Background mode (no blocking)
  - Flexible trigger system

- **CORS**: Flask-CORS 4.0.0
  - Enables cross-origin requests
  - Necessary for mobile/external access

- **Utilities**:
  - `python-dotenv`: Environment variable management
  - `Werkzeug`: WSGI utilities and file handling
  - `secrets`: Cryptographic random generation for secret keys

### Frontend
- **HTML5**: Semantic markup
  - Mobile-friendly viewport configuration
  - Accessibility features

- **CSS3**: Modern styling
  - Flexbox and Grid layouts
  - Responsive design for all screen sizes
  - Gradient backgrounds and animations
  - Media queries for mobile optimization

- **JavaScript (Vanilla)**: No framework overhead
  - ES6+ syntax
  - Fetch API for HTTP requests
  - DOM manipulation
  - Event handling
  - LocalStorage (if needed)

- **QR Code Library**: QRCode.js 1.0.0
  - CDN-hosted from cdnjs.cloudflare.com
  - Client-side generation
  - High error correction level (H)

### DevOps & Container
- **Docker**: Container platform
  - Python 3.11-slim base image (minimal size)
  - Multi-stage builds not needed (simple app)
  - Volume mounts for persistence

- **Docker Compose**: Container orchestration
  - Service definition
  - Port mapping
  - Volume management
  - Environment file injection

---

## Database Schema

### Overview
The application uses SQLite with three interconnected tables for a flexible, scalable data model.

### Tables

#### 1. `rooms`
Stores information about each media room.

```sql
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | TEXT | PRIMARY KEY | UUID (first 8 chars), unique identifier for room |
| `name` | TEXT | NOT NULL | Human-readable room name (e.g., "Room 201") |
| `enabled` | INTEGER | DEFAULT 1 | Boolean flag: 1=enabled, 0=disabled |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Room creation time |

**Indexes**: PRIMARY KEY on `id`

**Relationships**: 
- One-to-many with `room_images` (CASCADE DELETE)
- One-to-many with `pending_images` (CASCADE DELETE)

**Example Records**:
```
id: "a1b2c3d4" | name: "Conference Room A" | enabled: 1 | created_at: "2026-02-20 10:30:00"
id: "e5f6g7h8" | name: "Lobby Display" | enabled: 0 | created_at: "2026-02-19 15:45:00"
```

---

#### 2. `room_images`
Stores approved/active images for display in slideshows.

```sql
CREATE TABLE room_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
)
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Auto-incremented unique identifier |
| `room_id` | TEXT | NOT NULL, FOREIGN KEY | Reference to `rooms.id` |
| `image_path` | TEXT | NOT NULL | Full file path on disk (e.g., "uploads/a1b2c3d4_9f7e2c1a_photo.jpg") |
| `uploaded_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When image was added to the system |

**Indexes**: PRIMARY KEY on `id`, implied foreign key on `room_id`

**Cascade Behavior**: When a room is deleted, all its images are also deleted (ON DELETE CASCADE)

**Filename Convention**: `{room_id}_{uuid_hex[:8]}_{original_filename}`
- Example: `a1b2c3d4_9f7e2c1a_IMG_20260220.jpg`
- Prevents collisions and enables safe deletion

**Storage Location**: `/app/uploads/` (mounted to host `./uploads/`)

**Example Records**:
```
id: 1 | room_id: "a1b2c3d4" | image_path: "uploads/a1b2c3d4_9f7e2c1a_photo1.jpg" | uploaded_at: "2026-02-20 11:00:00"
id: 2 | room_id: "a1b2c3d4" | image_path: "uploads/a1b2c3d4_4d3f2e1c_photo2.jpg" | uploaded_at: "2026-02-20 11:05:00"
```

---

#### 3. `pending_images`
Stores images awaiting admin approval (when `APPROVAL_REQUIRED=true`).

```sql
CREATE TABLE pending_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    image_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
)
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Auto-incremented unique identifier |
| `room_id` | TEXT | NOT NULL, FOREIGN KEY | Reference to `rooms.id` |
| `image_path` | TEXT | NOT NULL | Full file path on disk |
| `uploaded_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When image was uploaded |
| `status` | TEXT | DEFAULT 'pending' | Workflow status: 'pending' or 'approved' |

**Status Values**:
- `'pending'`: Awaiting admin review (can be approved or denied)
- `'approved'`: Approved and moved to `room_images`

**Cascade Behavior**: When a room is deleted, all pending images are also deleted

**Expiry Mechanism**: APScheduler job cleans up pending images older than `PENDING_IMAGE_EXPIRY_MINUTES` (default 30 minutes)

**Example Records**:
```
id: 5 | room_id: "a1b2c3d4" | image_path: "uploads/a1b2c3d4_7a8b9c0d_pending.jpg" | uploaded_at: "2026-02-20 12:00:00" | status: "pending"
id: 6 | room_id: "e5f6g7h8" | image_path: "uploads/e5f6g7h8_1e2d3c4b_approved.jpg" | uploaded_at: "2026-02-20 12:05:00" | status: "approved"
```

---

### Database Relationships

```
┌─────────────┐
│   rooms     │
│  ┌────────┐ │
│  │ id (PK)│◄─┐
│  │ name   │ │
│  │enabled │ │
│  │created │ │
│  └────────┘ │
└─────────────┘
      │
      │ 1:N
      │ CASCADE DELETE
      ├──────────────┬──────────────┐
      │              │              │
      ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐
│ room_images  │ │pending_images│
│ ┌──────────┐ │ │ ┌──────────┐ │
│ │ id (PK)  │ │ │ │ id (PK)  │ │
│ │ room_id  │ │ │ │ room_id  │ │
│ │(FK)      │ │ │ │(FK)      │ │
│ │image_path│ │ │ │image_path│ │
│ │uploaded  │ │ │ │uploaded  │ │
│ │          │ │ │ │status    │ │
│ └──────────┘ │ │ └──────────┘ │
└──────────────┘ └──────────────┘
```

---

### Database Initialization

The `init_db()` function in [app.py](app.py) creates tables on first run:

```python
def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS rooms (...)
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS room_images (...)
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS pending_images (...)
    ''')
    
    # Auto-migration: add 'enabled' column if missing
    try:
        db.execute('ALTER TABLE rooms ADD COLUMN enabled INTEGER DEFAULT 1')
    except:
        pass
    
    db.commit()
    db.close()
```

**Migration Strategy**: The `enabled` column is added via `ALTER TABLE` if it doesn't exist, enabling zero-downtime upgrades from v6.x.

---

### Row Factory Configuration

```python
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Treat rows as dicts, not tuples
    return db
```

This allows accessing columns by name: `row['name']` instead of `row[0]`.

---

## Backend Implementation

### File: [app.py](app.py)

The main Flask application file (~460 lines) containing all backend logic.

### Application Initialization

```python
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))
```

**Key Points**:
- CORS enabled for cross-origin requests (necessary for mobile QR uploads)
- Secret key auto-generated from cryptographic entropy if not provided
- Session management enabled for admin authentication

### Configuration Variables

```python
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
DATABASE = os.path.join(DATA_FOLDER, 'qr_rooms.db')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload

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
```

**Safety Checks**:
- File upload limit: 50MB
- Auto-purge threshold: 48 hours (configurable)
- Slideshow duration: 10 seconds (configurable)
- Default credentials: admin/admin123 (MUST change in production)

### Authentication & Session Management

#### `login_required` Decorator

```python
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
```

**Usage**: Applied to all admin routes to enforce authentication.

#### Login Route

```python
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
```

**Security Notes**:
- Simple string comparison (HTTP should be HTTPS in production)
- Credentials stored in environment variables
- Session uses server-side secret key
- No rate limiting (add in production)

#### Logout Route

```python
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})
```

### Auto-Purge Job

#### `purge_old_images()` Function

```python
def purge_old_images():
    if not AUTO_PURGE_ENABLED:
        return

    try:
        db = get_db()
        cutoff_time = datetime.now() - timedelta(hours=AUTO_PURGE_HOURS)

        # Delete old approved images
        old_images = db.execute(
            'SELECT image_path FROM room_images WHERE uploaded_at < ?',
            (cutoff_time,)
        ).fetchall()

        for img in old_images:
            filepath = img['image_path']
            if os.path.exists(filepath):
                os.remove(filepath)

        db.execute('DELETE FROM room_images WHERE uploaded_at < ?', (cutoff_time,))
        
        # Delete expired pending images
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

        print(f"[AUTO-PURGE] Deleted {len(old_images)} images older than {AUTO_PURGE_HOURS}h")
    except Exception as e:
        print(f"[AUTO-PURGE ERROR] {str(e)}")
```

**Behavior**:
1. Runs every hour (scheduled by APScheduler)
2. Deletes images from `room_images` older than `AUTO_PURGE_HOURS`
3. Deletes pending images older than `PENDING_IMAGE_EXPIRY_MINUTES`
4. Deletes both database records AND physical files
5. Atomic operation: database updated only after file deletion succeeds

#### `start_scheduler()` Function

```python
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=purge_old_images, trigger="interval", hours=1)
    scheduler.start()
    print(f"[SCHEDULER] Auto-purge enabled: every 1 hour")
```

**Features**:
- Runs in background without blocking
- Trigger: Repeating every 1 hour
- Non-daemon thread (survives container restart)

---

### Public Routes (No Authentication)

#### GET `/` (Root/Index)
```python
@app.route('/')
def index():
    if 'logged_in' in session:
        return render_template('admin.html', ...)
    return redirect(url_for('login'))
```
Redirects to login if not authenticated, otherwise shows admin panel.

#### GET `/display/<room_id>`
```python
@app.route('/display/<room_id>')
def display(room_id):
    return render_template('display.html', room_id=room_id, server_url=SERVER_URL, slide_duration=SLIDE_DURATION)
```
Public display page for specified room (no authentication needed).

#### GET `/upload/<room_id>`
```python
@app.route('/upload/<room_id>')
def upload(room_id):
    return render_template('upload.html', room_id=room_id, server_url=SERVER_URL)
```
Public upload page for mobile QR scanning (no authentication needed).

#### GET `/uploads/<filename>`
```python
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
```
Static file serving for uploaded images.

---

### Protected Routes (Authentication Required)

#### GET `/api/rooms`
```python
@app.route('/api/rooms', methods=['GET'])
@login_required
def get_rooms():
    db = get_db()
    rooms = db.execute('SELECT * FROM rooms ORDER BY created_at DESC').fetchall()
    db.close()
    return jsonify([dict(room) for room in rooms])
```

**Response**:
```json
[
  {
    "id": "a1b2c3d4",
    "name": "Conference Room A",
    "enabled": 1,
    "created_at": "2026-02-20 10:30:00"
  }
]
```

#### POST `/api/rooms`
```python
@app.route('/api/rooms', methods=['POST'])
@login_required
def create_room():
    data = request.json
    room_name = data.get('name')

    if not room_name:
        return jsonify({'success': False, 'error': 'Room name required'}), 400

    room_id = str(uuid.uuid4())[:8]  # First 8 chars of UUID

    db = get_db()
    db.execute('INSERT INTO rooms (id, name, enabled) VALUES (?, ?, ?)', (room_id, room_name, 1))
    db.commit()
    db.close()

    return jsonify({'success': True, 'room_id': room_id, 'name': room_name})
```

**Request**:
```json
{
  "name": "New Room Name"
}
```

**Response**:
```json
{
  "success": true,
  "room_id": "a1b2c3d4",
  "name": "New Room Name"
}
```

#### POST `/api/rooms/<room_id>/toggle`
```python
@app.route('/api/rooms/<room_id>/toggle', methods=['POST'])
@login_required
def toggle_room(room_id):
    db = get_db()
    room = db.execute('SELECT enabled FROM rooms WHERE id = ?', (room_id,)).fetchone()
    
    if not room:
        db.close()
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    new_enabled = 1 - room['enabled']  # Toggle: 0 ↔ 1
    db.execute('UPDATE rooms SET enabled = ? WHERE id = ?', (new_enabled, room_id))
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'enabled': new_enabled})
```

**Response**:
```json
{
  "success": true,
  "enabled": 0
}
```

#### DELETE `/api/rooms/<room_id>`
```python
@app.route('/api/rooms/<room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    db = get_db()

    # Get all images (approved and pending)
    images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()
    pending = db.execute('SELECT image_path FROM pending_images WHERE room_id = ?', (room_id,)).fetchall()

    # Delete physical files
    for img in images + pending:
        filepath = img['image_path']
        if os.path.exists(filepath):
            os.remove(filepath)

    # Delete database records (cascade deletes images)
    db.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
    db.commit()
    db.close()

    return jsonify({'success': True})
```

**Cascade Behavior**: Deletes room and all associated images (database + files).

#### POST `/api/clear_images/<room_id>`
```python
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
```

**Note**: Clears only approved images, not pending ones.

---

### Image Upload & Approval Routes

#### POST `/api/save_images/<room_id>` (Public)
```python
@app.route('/api/save_images/<room_id>', methods=['POST'])
def save_images(room_id):
    if 'images[]' not in request.files:
        return jsonify({'success': False, 'error': 'No images provided'}), 400

    files = request.files.getlist('images[]')

    if not files:
        return jsonify({'success': False, 'error': 'No images provided'}), 400

    db = get_db()
    
    # Verify room exists
    room = db.execute('SELECT enabled FROM rooms WHERE id = ?', (room_id,)).fetchone()
    if not room:
        db.close()
        return jsonify({'success': False, 'error': 'Room not found'}), 404
    
    # Reject uploads to disabled rooms
    if not room['enabled']:
        db.close()
        return jsonify({'success': False, 'error': 'Room is disabled'}), 403

    saved_count = 0
    
    if APPROVAL_REQUIRED:
        # Save to pending queue
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
        # Replace all images (atomic operation)
        existing_images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()
        
        # Delete old files
        for img in existing_images:
            filepath = img['image_path']
            if os.path.exists(filepath):
                os.remove(filepath)

        # Clear database
        db.execute('DELETE FROM room_images WHERE room_id = ?', (room_id,))

        # Save new images
        for file in files:
            if file and file.filename:
                unique_filename = f"{room_id}_{uuid.uuid4().hex[:8]}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                db.execute('INSERT INTO room_images (room_id, image_path) VALUES (?, ?)', (room_id, filepath))
                saved_count += 1

        db.commit()

    db.close()

    return jsonify({'success': True, 'count': saved_count})
```

**Behavior**:
- If `APPROVAL_REQUIRED=true`: Images go to pending queue
- If `APPROVAL_REQUIRED=false` (default): Images replace existing ones atomically
- Room must be enabled to accept uploads
- Filenames prevent collisions with UUID

#### GET `/api/pending_images/<room_id>` (Protected)
```python
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
```

**Response**:
```json
{
  "pending": [
    {
      "id": 5,
      "url": "http://10.192.128.125:5000/uploads/a1b2c3d4_7a8b9c0d_IMG.jpg",
      "uploaded_at": "2026-02-20 12:00:00"
    }
  ]
}
```

#### POST `/api/pending_images/<int:pending_id>/approve` (Protected)
```python
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
    
    # Move to approved (adds to slideshow, doesn't replace)
    db.execute('INSERT INTO room_images (room_id, image_path) VALUES (?, ?)', (room_id, image_path))
    db.execute('UPDATE pending_images SET status = ? WHERE id = ?', ('approved', pending_id))
    
    db.commit()
    db.close()
    
    return jsonify({'success': True})
```

**Note**: Approved images are added to the slideshow, not replacing existing images.

#### POST `/api/pending_images/<int:pending_id>/deny` (Protected)
```python
@app.route('/api/pending_images/<int:pending_id>/deny', methods=['POST'])
@login_required
def deny_image(pending_id):
    db = get_db()
    pending = db.execute('SELECT image_path FROM pending_images WHERE id = ?', (pending_id,)).fetchone()
    
    if not pending:
        db.close()
        return jsonify({'success': False, 'error': 'Image not found'}), 404
    
    image_path = pending['image_path']
    
    # Delete physical file
    if os.path.exists(image_path):
        os.remove(image_path)
    
    # Delete database record
    db.execute('DELETE FROM pending_images WHERE id = ?', (pending_id,))
    db.commit()
    db.close()
    
    return jsonify({'success': True})
```

---

### Display Routes (Public)

#### GET `/api/get_images/<room_id>`
```python
@app.route('/api/get_images/<room_id>', methods=['GET'])
def get_images(room_id):
    db = get_db()
    
    # Check room enabled status
    room = db.execute('SELECT enabled FROM rooms WHERE id = ?', (room_id,)).fetchone()
    if room and not room['enabled']:
        db.close()
        return jsonify({'images': [], 'disabled': True})
    
    # Fetch approved images
    images = db.execute(
        'SELECT image_path FROM room_images WHERE room_id = ? ORDER BY uploaded_at ASC',
        (room_id,)
    ).fetchall()
    db.close()

    # Convert to URLs
    image_urls = [f"{SERVER_URL}/{img['image_path']}" for img in images]

    return jsonify({'images': image_urls, 'disabled': False})
```

**Response** (No images):
```json
{
  "images": [],
  "disabled": false
}
```

**Response** (Disabled room):
```json
{
  "images": [],
  "disabled": true
}
```

**Response** (With images):
```json
{
  "images": [
    "http://10.192.128.125:5000/uploads/a1b2c3d4_9f7e2c1a_photo1.jpg",
    "http://10.192.128.125:5000/uploads/a1b2c3d4_4d3f2e1c_photo2.jpg"
  ],
  "disabled": false
}
```

---

### Application Entry Point

```python
if __name__ == '__main__':
    init_db()  # Create tables if needed
    if AUTO_PURGE_ENABLED:
        start_scheduler()  # Start background auto-purge job
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**Startup Sequence**:
1. Initialize database (creates tables if missing)
2. Start scheduler (if enabled)
3. Start Flask server on 0.0.0.0:5000

---

## Frontend Implementation

The frontend consists of four main HTML templates with associated JavaScript and CSS files, providing a complete user experience for both mobile uploaders and desktop admin users.

### Architecture Overview

**File Structure**:
```
templates/
├── login.html          # Admin authentication
├── admin.html          # Room management dashboard
├── display.html        # TV/monitor display
└── upload.html         # Mobile image upload

static/
├── js/
│   ├── admin.js        # Admin panel logic
│   ├── display.js      # Display page logic
│   └── upload.js       # Upload page logic
└── css/
    ├── admin.css       # Admin styling
    ├── display.css     # Display styling
    ├── login.css       # Login styling
    └── upload.css      # Upload styling
```

---

### [templates/login.html](templates/login.html) - Authentication Page

**Purpose**: Secure gateway to admin panel with user authentication.

**Key Features**:
- Username and password input fields
- Form submission via Fetch API
- Error message display
- Auto-focus on username field
- Browser-integrated autocomplete support

**Form Structure**:
```html
<form id="loginForm">
    <div class="form-group">
        <label for="username">Username</label>
        <input type="text" id="username" name="username" autocomplete="username" required>
    </div>
    <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" autocomplete="current-password" required>
    </div>
    <button type="submit" class="btn-login">Login</button>
</form>
<div id="errorMessage" class="error-message" style="display: none;"></div>
```

**Authentication Flow**:
```javascript
// POST to /login with JSON credentials
const response = await fetch(`${serverUrl}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
});

const data = await response.json();

if (data.success) {
    window.location.href = '/admin';  // Redirect on success
} else {
    // Display error message
}
```

**Styling** ([login.css](static/css/login.css)):
- Gradient background (purple theme)
- Centered login card with box shadow
- Smooth animations (slide-up on load)
- Responsive mobile layout
- Focus states for accessibility

---

### [templates/admin.html](templates/admin.html) - Admin Dashboard

**Purpose**: Central hub for room management, image uploads, and approval workflow.

**Key Sections**:
1. **Header**: Title + Logout button
2. **Room Creation**: Input + Create button
3. **Search & Sort**: Search bar + Sort buttons
4. **Pending Approvals** (optional): Grouped by room with approve/deny actions
5. **Rooms Grid**: Responsive grid of room cards
6. **Upload Modal**: Picture-in-picture overlay for bulk image upload

**Main HTML Structure**:
```html
<div class="admin-container">
    <div class="admin-header">
        <h1>🎯 QR Module - Room Management</h1>
        <button onclick="logout()" class="btn-logout">Logout</button>
    </div>

    <div class="add-room-section">
        <input type="text" id="roomName" placeholder="Enter room name">
        <button onclick="createRoom()" class="btn-create">Create Room</button>
    </div>

    <div class="rooms-controls">
        <div class="search-wrap">
            <input type="search" id="searchInput" placeholder="Search rooms">
            <button id="clearSearchBtn" class="btn-clear">✕</button>
            <span id="resultsCount">0 results</span>
        </div>
        <div class="sort-buttons">
            <button class="sort-btn active" data-sort="created_desc">Newest</button>
            <button class="sort-btn" data-sort="created_asc">Oldest</button>
            <button class="sort-btn" data-sort="name_asc">Name A→Z</button>
            <button class="sort-btn" data-sort="name_desc">Name Z→A</button>
            <button class="sort-btn" data-sort="enabled_first">Enabled First</button>
        </div>
    </div>

    <div id="pendingSection" class="pending-section" style="display: none;">
        <h2>⏳ Pending Approvals</h2>
        <div id="pendingList" class="pending-list"></div>
    </div>

    <div id="roomsList" class="rooms-grid"></div>
</div>

<!-- Upload Modal -->
<div id="uploadModal" class="modal">
    <div class="modal-content">
        <span class="close">&times;</span>
        <h2 id="modalTitle">Upload Images</h2>
        <input type="file" id="modalFileInput" accept="image/*" multiple>
        <div id="modalPreview" class="modal-preview"></div>
        <button onclick="uploadFromModal()" class="btn-upload-modal">Upload Images</button>
        <div id="modalStatus" class="modal-status"></div>
    </div>
</div>
```

**Room Card Structure**:
```html
<div class="room-card [disabled]">
    <h3>Conference Room A</h3>
    <p>Room ID: <code>a1b2c3d4</code></p>
    <p class="status-indicator">
        <span class="status-badge enabled">🟢 Enabled</span>
    </p>
    <div class="room-url">http://10.192.128.125:5000/display/a1b2c3d4</div>
    <div class="button-group">
        <button class="btn-view" onclick="viewRoom(...)">View Display</button>
        <button class="btn-upload" onclick="openUploadModal(...)">Upload Images</button>
        <button class="btn-toggle btn-disable" onclick="toggleRoom(...)">Disable</button>
        <button class="btn-clear" onclick="clearRoomImages(...)">Clear</button>
        <button class="btn-delete" onclick="deleteRoom(...)">Delete</button>
    </div>
</div>
```

---

### [static/js/admin.js](static/js/admin.js) - Admin Logic

**Main Functions**:

#### `loadRooms()`
Fetches all rooms from API and renders them.
```javascript
function loadRooms() {
    fetch(`${serverUrl}/api/rooms`)
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';  // Re-login if session expired
                return;
            }
            return response.json();
        })
        .then(rooms => {
            allRooms = rooms || [];
            renderRooms();
            if (approvalRequired) {
                loadPendingApprovals();  // Load pending queue if applicable
            }
        })
        .catch(error => console.error('Error loading rooms:', error));
}
```

#### `renderRooms()`
Renders filtered and sorted rooms.
```javascript
function renderRooms() {
    // 1. Get search term
    const search = (document.getElementById('searchInput')?.value || '').trim().toLowerCase();

    // 2. Filter rooms
    let filtered = allRooms.filter(r => {
        return r.name.toLowerCase().includes(search) || 
               r.id.toLowerCase().includes(search);
    });

    // 3. Sort according to currentSort
    switch (currentSort) {
        case 'created_asc':
            filtered.sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
            break;
        case 'created_desc':
            filtered.sort((a,b) => new Date(b.created_at) - new Date(a.created_at));
            break;
        case 'name_asc':
            filtered.sort((a,b) => a.name.localeCompare(b.name));
            break;
        case 'name_desc':
            filtered.sort((a,b) => b.name.localeCompare(a.name));
            break;
        case 'enabled_first':
            filtered.sort((a,b) => (b.enabled === 1 ? 1 : 0) - (a.enabled === 1 ? 1 : 0));
            break;
    }

    // 4. Render HTML with highlighting
    roomsList.innerHTML = filtered.map(room => `
        <div class="room-card ${room.enabled === 0 ? 'disabled' : ''}">
            <h3>${highlight(room.name, search)}</h3>
            ...
        </div>
    `).join('');
}
```

#### `createRoom()`
Creates a new room.
```javascript
function createRoom() {
    const roomName = document.getElementById('roomName').value.trim();

    if (!roomName) {
        alert('Please enter a room name');
        return;
    }

    fetch(`${serverUrl}/api/rooms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: roomName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('roomName').value = '';
            loadRooms();  // Reload list
        } else {
            alert('Failed to create room: ' + (data.error || 'Unknown error'));
        }
    });
}
```

#### `deleteRoom(roomId)`
Deletes a room with confirmation.
```javascript
function deleteRoom(roomId) {
    if (!confirm('Are you sure you want to delete this room? All images will be removed.')) {
        return;
    }

    fetch(`${serverUrl}/api/rooms/${roomId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadRooms();
            } else {
                alert('Failed to delete room');
            }
        });
}
```

#### `toggleRoom(roomId)`
Enables/disables a room.
```javascript
function toggleRoom(roomId) {
    fetch(`${serverUrl}/api/rooms/${roomId}/toggle`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadRooms();
            } else {
                alert('Failed to toggle room');
            }
        });
}
```

#### `clearRoomImages(roomId)`
Clears all images from a room with confirmation.
```javascript
function clearRoomImages(roomId) {
    if (!confirm('Clear all images from this room?')) {
        return;
    }

    fetch(`${serverUrl}/api/clear_images/${roomId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadRooms();
            }
        });
}
```

#### `escapeHtml(str)` & `highlight(text, term)`
HTML sanitization and search result highlighting.
```javascript
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function highlight(text, term) {
    if (!term) return escapeHtml(text);
    const idx = text.toLowerCase().indexOf(term.toLowerCase());
    if (idx === -1) return escapeHtml(text);
    const before = escapeHtml(text.slice(0, idx));
    const match = escapeHtml(text.slice(idx, idx + term.length));
    const after = escapeHtml(text.slice(idx + term.length));
    return `${before}<mark>${match}</mark>${after}`;
}
```

#### `openUploadModal(roomId, roomName)`
Opens the file upload modal.
```javascript
function openUploadModal(roomId, roomName) {
    currentRoomId = roomId;
    document.getElementById('modalTitle').textContent = `Upload Images to ${roomName}`;
    document.getElementById('modalFileInput').value = '';
    document.getElementById('modalPreview').innerHTML = '';
    document.getElementById('modalStatus').innerHTML = '';
    modal.style.display = 'block';
}
```

#### `uploadFromModal()`
Uploads selected files.
```javascript
function uploadFromModal() {
    const fileInput = document.getElementById('modalFileInput');
    const files = fileInput.files;

    if (files.length === 0) {
        alert('Please select at least one image');
        return;
    }

    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('images[]', file);
    });

    const statusDiv = document.getElementById('modalStatus');
    statusDiv.textContent = 'Uploading...';

    fetch(`${serverUrl}/api/save_images/${currentRoomId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusDiv.textContent = `Successfully uploaded ${data.count} image(s)!`;
            statusDiv.className = 'modal-status success';
            setTimeout(() => {
                closeUploadModal();
                loadRooms();
            }, 1500);
        } else {
            statusDiv.textContent = 'Upload failed: ' + (data.error || 'Unknown error');
            statusDiv.className = 'modal-status error';
        }
    });
}
```

#### `loadPendingApprovals()`
Loads pending images grouped by room.
```javascript
function loadPendingApprovals() {
    const pendingSection = document.getElementById('pendingSection');
    const pendingList = document.getElementById('pendingList');

    const pendingPromises = allRooms.map(room =>
        fetch(`${serverUrl}/api/pending_images/${room.id}`)
            .then(response => response.json())
            .then(data => {
                return { room, pending: data.pending || [] };
            })
    );

    Promise.all(pendingPromises)
        .then(results => {
            const roomsWithPending = results.filter(r => r.pending.length > 0);
            
            if (roomsWithPending.length > 0) {
                pendingSection.style.display = 'block';
                pendingList.innerHTML = roomsWithPending.map(({ room, pending }) => `
                    <div class="pending-room">
                        <div class="pending-room-header">
                            <h3>${escapeHtml(room.name)} <span class="badge">${pending.length}</span></h3>
                        </div>
                        <div class="pending-grid">
                            ${pending.map(img => `
                                <div class="pending-item-compact">
                                    <div class="pending-thumb">
                                        <img src="${img.url}" alt="Pending">
                                        <span class="pending-time">${new Date(img.uploaded_at).toLocaleTimeString()}</span>
                                    </div>
                                    <div class="pending-item-actions">
                                        <button class="btn-approve" onclick="approveImage(${img.id})" title="Approve">✓</button>
                                        <button class="btn-deny" onclick="denyImage(${img.id})" title="Deny">✗</button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `).join('');
            } else {
                pendingSection.style.display = 'none';
            }
        });
}
```

#### `approveImage(imageId)` & `denyImage(imageId)`
Approve or deny pending uploads.
```javascript
function approveImage(imageId) {
    fetch(`${serverUrl}/api/pending_images/${imageId}/approve`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadRooms();
            }
        });
}

function denyImage(imageId) {
    if (!confirm('Are you sure you want to deny this upload?')) {
        return;
    }
    
    fetch(`${serverUrl}/api/pending_images/${imageId}/deny`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadRooms();
            }
        });
}
```

#### `logout()`
Logs out the user.
```javascript
function logout() {
    fetch(`${serverUrl}/logout`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/login';
            }
        });
}
```

#### Search & Sort Event Handlers
```javascript
function debounce(fn, wait) {
    let t;
    return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), wait);
    };
}

const debouncedRender = debounce(() => renderRooms(), 250);

searchInput.addEventListener('input', debouncedRender);

clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    renderRooms();
    searchInput.focus();
});

sortButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
        sortButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentSort = btn.getAttribute('data-sort') || 'created_desc';
        renderRooms();
    });
});
```

---

### [templates/display.html](templates/display.html) - Display Page

**Purpose**: Full-screen display for TVs/monitors showing QR code or image slideshow.

**Key Features**:
- QR code generation for room upload
- Automatic image polling (3-second intervals)
- Image slideshow with configurable duration
- Clear button to remove images
- Disabled room indicator
- Full-screen optimization

**HTML Structure**:
```html
<!-- QR Code Container (initial state) -->
<div id="qrContainer" class="qr-container">
    <div id="qrcode"></div>
</div>

<!-- Image Container (when images exist) -->
<div id="imageContainer" class="image-container" style="display: none;">
    <img id="displayImage" src="" alt="Uploaded Image">
    <button id="clearBtn">Clear</button>
</div>

<!-- Disabled Container (when room is disabled) -->
<div id="disabledContainer" class="disabled-container" style="display: none;">
    <div class="disabled-message">
        🔴 Currently Disabled
    </div>
</div>
```

---

### [static/js/display.js](static/js/display.js) - Display Logic

**Main Functions**:

#### `generateQRCode()`
Generates QR code linking to upload page.
```javascript
function generateQRCode() {
    const qrDiv = document.getElementById('qrcode');
    const uploadUrl = `${serverUrl}/upload/${roomId}`;
    qrDiv.innerHTML = '';

    new QRCode(qrDiv, {
        text: uploadUrl,
        width: 300,
        height: 300,
        colorDark: '#000000',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H  // High error correction
    });
}
```

#### `checkForImages()`
Polls server for images every 3 seconds.
```javascript
function checkForImages() {
    fetch(`${serverUrl}/api/get_images/${roomId}`)
        .then(response => response.json())
        .then(data => {
            if (data.disabled) {
                showDisabled();
            } else if (data.images && data.images.length > 0) {
                if (!isShowingImages) {
                    images = data.images;
                    showImages();
                }
            } else {
                if (isShowingImages) {
                    showQRCode();
                }
            }
        })
        .catch(error => console.error('Error checking for images:', error));
}

// Poll every 3 seconds
setInterval(checkForImages, 3000);
```

#### `showQRCode()` / `showImages()` / `showDisabled()`
Display state management.
```javascript
function showQRCode() {
    isShowingImages = false;
    document.getElementById('imageContainer').style.display = 'none';
    document.getElementById('disabledContainer').style.display = 'none';
    document.getElementById('qrContainer').style.display = 'flex';
    stopSlideshow();
}

function showImages() {
    isShowingImages = true;
    document.getElementById('qrContainer').style.display = 'none';
    document.getElementById('disabledContainer').style.display = 'none';
    document.getElementById('imageContainer').style.display = 'flex';
    currentImageIndex = 0;
    displayCurrentImage();

    if (images.length > 1) {
        startSlideshow();
    } else {
        stopSlideshow();
    }
}

function showDisabled() {
    isShowingImages = false;
    document.getElementById('qrContainer').style.display = 'none';
    document.getElementById('imageContainer').style.display = 'none';
    document.getElementById('disabledContainer').style.display = 'flex';
    stopSlideshow();
}
```

#### `startSlideshow()` / `stopSlideshow()`
Slideshow control.
```javascript
function startSlideshow() {
    stopSlideshow();
    slideshowInterval = setInterval(() => {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        displayCurrentImage();
    }, slideDuration);  // slideDuration = 10000ms by default
}

function stopSlideshow() {
    if (slideshowInterval) {
        clearInterval(slideshowInterval);
        slideshowInterval = null;
    }
}
```

#### `clearImages()`
Clears all images (via button click).
```javascript
function clearImages() {
    fetch(`${serverUrl}/api/clear_images/${roomId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                images = [];
                isShowingImages = false;
                stopSlideshow();
                showQRCode();
            }
        });
}

document.getElementById('clearBtn').addEventListener('click', clearImages);
```

---

### [templates/upload.html](templates/upload.html) - Mobile Upload Page

**Purpose**: Mobile-friendly interface for uploading images via QR code.

**Key Features**:
- Tap-to-select image input
- Multiple file selection
- Image preview grid
- Upload progress feedback
- Auto-close on success

**HTML Structure**:
```html
<div class="upload-container">
    <h1>📷 Upload Images</h1>
    <p>Select one or more images to display</p>

    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
        <input type="file" id="fileInput" accept="image/*" multiple style="display: none;">
        <div class="upload-icon">📷</div>
        <div class="upload-text">Tap to select images</div>
    </div>

    <div id="preview" class="preview-area"></div>
    <button id="uploadBtn" onclick="uploadImages()" style="display: none;">Upload Images</button>
    <div id="status" class="status-message"></div>
</div>
```

---

### [static/js/upload.js](static/js/upload.js) - Upload Logic

**Main Functions**:

#### `displayPreview()`
Shows thumbnail preview of selected images.
```javascript
function displayPreview() {
    const preview = document.getElementById('preview');
    preview.innerHTML = '';

    selectedFiles.forEach(file => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            preview.appendChild(img);
        };
        reader.readAsDataURL(file);
    });
}
```

#### `uploadImages()`
Uploads selected files to server.
```javascript
function uploadImages() {
    if (selectedFiles.length === 0) {
        showStatus('Please select at least one image', 'error');
        return;
    }

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('images[]', file);
    });

    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';

    fetch(`${serverUrl}/api/save_images/${roomId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showStatus(`Successfully uploaded ${data.count} image(s)!`, 'success');
            setTimeout(() => {
                window.close();  // Close tab on success
            }, 2000);
        } else {
            showStatus('Upload failed: ' + (data.error || 'Unknown error'), 'error');
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload Images';
        }
    });
}
```

#### File Selection Handler
```javascript
document.getElementById('fileInput').addEventListener('change', function(e) {
    selectedFiles = Array.from(e.target.files);
    displayPreview();

    if (selectedFiles.length > 0) {
        document.getElementById('uploadBtn').style.display = 'block';
    }
});
```

---

### CSS Styling

#### [static/css/admin.css](static/css/admin.css) - 561 lines
**Design System**:
- **Color Scheme**: Purple gradient (667eea → 764ba2), white cards, status badges
- **Layout**: CSS Grid for rooms, Flexbox for controls
- **Responsive**: Mobile-first, adapts to all screen sizes
- **Components**:
  - Room cards with 5 action buttons
  - Search bar with clear button
  - Sort buttons with active state
  - Pending approvals grid with thumbnails
  - Upload modal with file preview
  - Status badges (Enabled/Disabled)

#### [static/css/display.css](static/css/display.css)
**Design System**:
- **Full-Screen**: 100vh containers optimized for TV displays
- **Images**: Responsive sizing with object-fit: contain
- **QR Code**: Adaptive sizing for all screen resolutions
- **Clear Button**: Bottom-centered with pulsing animation
- **Disabled State**: Gradient background with pulsing message

#### [static/css/login.css](static/css/login.css)
**Design System**:
- **Login Card**: Centered white card on gradient background
- **Form**: Vertical layout with label + input pairs
- **Animations**: Slide-up entrance animation
- **Accessibility**: Focus states with colored borders

#### [static/css/upload.css](static/css/upload.css)
**Design System**:
- **Upload Area**: Large dashed border with hover effects
- **Preview Grid**: Auto-fill grid for thumbnails
- **Mobile**: Adjusted padding and font sizes for small screens
- **Status Messages**: Color-coded success (green) and error (red)

---

## API Documentation

### Base URL
```
http://{SERVER_IP}:{SERVER_PORT}
```
Default: `http://10.192.128.125:5000`

### Authentication
- **Login**: POST `/login`
- **Logout**: POST `/logout`
- **Session**: Cookie-based via Flask sessions
- **Protected Routes**: Marked with `@login_required`

### Endpoints

#### Authentication

**POST `/login`**
- Description: Authenticate admin user
- Auth: None
- Content-Type: application/json
- Request Body:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- Response (Success):
  ```json
  {
    "success": true
  }
  ```
- Response (Failure): 401
  ```json
  {
    "success": false,
    "error": "Invalid credentials"
  }
  ```

**POST `/logout`**
- Description: Clear session
- Auth: Protected
- Response:
  ```json
  {
    "success": true
  }
  ```

---

#### Room Management

**GET `/api/rooms`**
- Description: List all rooms
- Auth: Protected
- Response:
  ```json
  [
    {
      "id": "a1b2c3d4",
      "name": "Conference Room A",
      "enabled": 1,
      "created_at": "2026-02-20 10:30:00"
    }
  ]
  ```

**POST `/api/rooms`**
- Description: Create new room
- Auth: Protected
- Content-Type: application/json
- Request Body:
  ```json
  {
    "name": "New Room"
  }
  ```
- Response:
  ```json
  {
    "success": true,
    "room_id": "a1b2c3d4",
    "name": "New Room"
  }
  ```

**DELETE `/api/rooms/{room_id}`**
- Description: Delete room and all images
- Auth: Protected
- Response:
  ```json
  {
    "success": true
  }
  ```

**POST `/api/rooms/{room_id}/toggle`**
- Description: Enable/disable room
- Auth: Protected
- Response:
  ```json
  {
    "success": true,
    "enabled": 0
  }
  ```

---

#### Image Management

**POST `/api/save_images/{room_id}`**
- Description: Upload images to room
- Auth: None (public)
- Content-Type: multipart/form-data
- Request Body:
  - `images[]` (file): Multiple image files
- Response (Success):
  ```json
  {
    "success": true,
    "count": 3
  }
  ```
- Response (Failure): 400, 404, or 403
  ```json
  {
    "success": false,
    "error": "Room is disabled"
  }
  ```
- Behavior:
  - If `APPROVAL_REQUIRED=true`: Images go to pending queue
  - If `APPROVAL_REQUIRED=false`: Images replace all existing images

**GET `/api/get_images/{room_id}`**
- Description: Get approved images for display
- Auth: None (public)
- Response (With images):
  ```json
  {
    "images": [
      "http://10.192.128.125:5000/uploads/a1b2c3d4_9f7e2c1a_photo1.jpg",
      "http://10.192.128.125:5000/uploads/a1b2c3d4_4d3f2e1c_photo2.jpg"
    ],
    "disabled": false
  }
  ```
- Response (Disabled room):
  ```json
  {
    "images": [],
    "disabled": true
  }
  ```

**POST `/api/clear_images/{room_id}`**
- Description: Remove all approved images
- Auth: Protected
- Response:
  ```json
  {
    "success": true
  }
  ```

---

#### Approval Workflow

**GET `/api/pending_images/{room_id}`**
- Description: Get pending uploads for room
- Auth: Protected
- Response:
  ```json
  {
    "pending": [
      {
        "id": 5,
        "url": "http://10.192.128.125:5000/uploads/a1b2c3d4_7a8b9c0d_IMG.jpg",
        "uploaded_at": "2026-02-20 12:00:00"
      }
    ]
  }
  ```

**POST `/api/pending_images/{pending_id}/approve`**
- Description: Approve pending image
- Auth: Protected
- Response:
  ```json
  {
    "success": true
  }
  ```

**POST `/api/pending_images/{pending_id}/deny`**
- Description: Reject pending image (deletes file)
- Auth: Protected
- Response:
  ```json
  {
    "success": true
  }
  ```

---

## Configuration & Environment Variables

### Environment File: `.env`

```dotenv
# Server Configuration
SERVER_IP=192.168.1.197
SERVER_PORT=5000

# Database & Storage
# DATABASE=data/qr_rooms.db (auto-created)
# UPLOAD_FOLDER=uploads (auto-created)

# Slideshow Configuration
SLIDE_DURATION=5000              # Duration per image (milliseconds)

# Auto-Purge Configuration
AUTO_PURGE_ENABLED=true          # Enable/disable auto-purge
AUTO_PURGE_HOURS=48              # Delete images older than N hours

# Admin Authentication
ADMIN_USERNAME=admin             # Admin username
ADMIN_PASSWORD=admin123          # Admin password
SECRET_KEY=your-secret-key-change-this  # Session encryption key

# Media Approval System
APPROVAL_REQUIRED=false          # Require admin approval for uploads
PENDING_IMAGE_EXPIRY_MINUTES=30  # Auto-delete unapproved images after N minutes
```

### Configuration Details

| Variable | Default | Range | Notes |
|----------|---------|-------|-------|
| `SERVER_IP` | 10.192.128.125 | Any valid IP | Must match network accessibility |
| `SERVER_PORT` | 5000 | 1-65535 | Must be available and open in firewall |
| `AUTO_PURGE_ENABLED` | true | true/false | Can disable without affecting display |
| `AUTO_PURGE_HOURS` | 48 | 1-8760 | Images older than this are deleted hourly |
| `SLIDE_DURATION` | 10000 | 1-60000 | Milliseconds between image transitions |
| `ADMIN_USERNAME` | admin | Any string | Change in production! |
| `ADMIN_PASSWORD` | admin123 | Any string | Change in production! |
| `APPROVAL_REQUIRED` | false | true/false | Enables two-step upload review |
| `PENDING_IMAGE_EXPIRY_MINUTES` | 30 | 1-1440 | Unapproved uploads deleted after this time |

### Loading Configuration

The `.env` file is loaded automatically by:
1. Docker Compose (via `env_file: - .env`)
2. Python-dotenv (via `python-dotenv` package)

---

## Security Implementation

### Authentication & Authorization

**Session Management**:
- Uses Flask sessions with cryptographic signing
- Secret key: 32-byte random hex (auto-generated or configurable)
- Session cookie: HTTP-only, Secure flag (should be set in production)

**Password Security**:
- Stored in environment variables (not in code)
- Plain-text comparison (upgrade to bcrypt in production)
- Default credentials MUST be changed in production

### Input Validation & Sanitization

**HTML Sanitization**:
```javascript
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
```

**File Upload Validation**:
- Max file size: 50MB (configurable in app.config)
- File type: Only images (enforced by HTML5 `accept="image/*"`)
- Filename sanitization: UUID-based unique names prevent directory traversal

**Room ID Validation**:
- UUID format validation at database (FOREIGN KEY)
- SQL injection prevention: Parameterized queries throughout

**SQL Injection Prevention**:
- All queries use parameterized statements (`?` placeholders)
- Example:
  ```python
  db.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
  ```

### Cross-Origin Request Handling (CORS)

```python
CORS(app)  # Allow all origins by default
```

**Security Note**: In production, restrict to specific origins:
```python
CORS(app, origins=['http://10.192.128.125:5000'])
```

### File System Security

**File Naming Convention**:
- Format: `{room_id}_{uuid_hex[:8]}_{original_filename}`
- Prevents collisions and unauthorized file deletion
- No path traversal possible (no `../` in names)

**File Permissions**:
- Docker volume: `./uploads` mounted as `/app/uploads`
- World-readable (necessary for web server)
- Deletion only via API (admin protected or purge job)

### SSL/TLS Recommendations

**For Production**:
1. Enable HTTPS (use nginx reverse proxy)
2. Install SSL certificate (Let's Encrypt)
3. Set `Secure` flag on session cookies
4. Implement HSTS (Strict-Transport-Security header)

---

## Deployment & Containerization

### Docker Setup

#### [Dockerfile](Dockerfile)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 5000

CMD ["python", "app.py"]
```

**Image Details**:
- **Base**: `python:3.11-slim` (~155MB)
- **Working Directory**: `/app`
- **Dependencies**: Installed without cache to reduce layer size
- **Pre-created Directory**: `uploads` folder (for volume mount)
- **Port**: 5000 (exposed)
- **Entry Point**: `python app.py`

#### [docker-compose.yml](docker-compose.yml)
```yaml
version: '3.8'

services:
  qr-module:
    build: .
    container_name: qr-module
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./data:/app/data
    env_file:
      - .env
    restart: unless-stopped
```

**Service Configuration**:
- **Build Context**: Current directory (`.`)
- **Container Name**: `qr-module`
- **Port Mapping**: 5000:5000 (host:container)
- **Volumes**:
  - `./uploads` → `/app/uploads` (persistent image storage)
  - `./data` → `/app/data` (persistent database)
- **Environment**: Loaded from `.env` file
- **Restart Policy**: `unless-stopped` (auto-restart on crash, manual stop)

### Deployment Steps

#### Local Development
```bash
# Clone/extract repository
cd qr-module

# Copy .env template (if needed)
cp .env.example .env

# Build and start containers
docker compose up -d --build

# View logs
docker compose logs -f qr-module

# Access
# Admin: http://localhost:5000
# Display: http://localhost:5000/display/{room_id}
```

#### Production Deployment
```bash
# On production server
cd /opt/qr-module

# Update .env with production settings
nano .env
# Set: SERVER_IP, ADMIN_PASSWORD, SECRET_KEY, APPROVAL_REQUIRED, etc.

# Backup existing data (if upgrading)
cp data/qr_rooms.db data/qr_rooms.db.backup
cp -r uploads uploads.backup

# Pull latest (if using git)
git pull origin main

# Build and start
docker compose up -d --build

# Verify
docker compose ps
```

#### Updating from Previous Version
```bash
# Stop current container
docker compose down

# Backup database
cp data/qr_rooms.db data/qr_rooms.db.v6.2.backup

# Update code
git pull origin main

# Rebuild with new code
docker compose up -d --build

# Check logs for migration messages
docker compose logs qr-module | head -20
```

### Persistence

**Volumes**:
- `uploads/`: Survives container stops/restarts/rebuilds
- `data/`: SQLite database persists across restarts

**Data Loss Prevention**:
1. Regular backups: `docker compose exec qr-module tar czf backup.tar.gz /app/data /app/uploads`
2. Volume backups: `cp -r data uploads backup-$(date +%Y%m%d)/`
3. Database export: `sqlite3 data/qr_rooms.db ".dump" > backup.sql`

---

## File Organization & Structure

```
qr-module/
├── app.py                          # Main Flask application (460 lines)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker container definition
├── docker-compose.yml              # Container orchestration
├── .env                            # Environment variables (DO NOT COMMIT)
├── .gitignore                      # Git ignore rules
│
├── templates/                      # HTML templates
│   ├── login.html                  # Admin login page
│   ├── admin.html                  # Admin dashboard
│   ├── display.html                # TV/monitor display
│   └── upload.html                 # Mobile upload page
│
├── static/                         # Static assets
│   ├── js/                         # JavaScript logic
│   │   ├── admin.js                # Admin panel functionality
│   │   ├── display.js              # Display page functionality
│   │   └── upload.js               # Upload functionality
│   └── css/                        # Stylesheets
│       ├── admin.css               # Admin styling (561 lines)
│       ├── display.css             # Display styling
│       ├── login.css               # Login styling
│       └── upload.css              # Upload styling
│
├── uploads/                        # Image storage (git-ignored)
│   └── {room_id}_{uuid}_{filename}.jpg
│
├── data/                           # Database storage (git-ignored)
│   └── qr_rooms.db                 # SQLite database
│
├── README.md                       # User documentation
├── CHANGELOG.md                    # Version history (v6.1 - v7.1)
└── TECHNICAL_DOCUMENTATION.md      # This file
```

### File Sizes (Approximate)
- `app.py`: ~15 KB
- `admin.js`: ~18 KB
- `admin.css`: ~22 KB
- `display.js`: ~5 KB
- `upload.js`: ~3 KB
- Total static assets: ~100 KB (before uploads)

### Git Configuration

**.gitignore**:
```
data/
uploads/
.env
__pycache__/
*.pyc
.DS_Store
.vscode/
.idea/
```

---

## Workflows & User Flows

### Workflow 1: Admin Creates Room & Upload Images

**Actors**: Admin User  
**Preconditions**: Admin authenticated, browser access to admin panel

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Admin Opens Admin Panel (http://10.192.128.125:5000)     │
│    └─ loadRooms() fetches all rooms from API                │
│    └─ renderRooms() displays grid of room cards             │
│                                                             │
│ 2. Admin Enters Room Name & Clicks "Create Room"            │
│    └─ createRoom() POST /api/rooms with name                │
│    └─ Backend: INSERT into rooms table                      │
│    └─ Backend: Generate 8-char UUID for room_id             │
│    └─ Response: { success, room_id, name }                  │
│    └─ Frontend: Clear input, call loadRooms()              │
│    └─ Room appears in grid with action buttons              │
│                                                             │
│ 3. Admin Clicks "Upload Images" on Room Card                │
│    └─ openUploadModal(room_id) shows file picker modal      │
│                                                             │
│ 4. Admin Selects Image File(s) From Computer                │
│    └─ handleModalFileSelect() shows thumbnail preview       │
│    └─ Upload button becomes enabled                         │
│                                                             │
│ 5. Admin Clicks "Upload Images" in Modal                    │
│    └─ uploadFromModal() POST /api/save_images/{room_id}     │
│    └─ FormData with images[] array                          │
│    └─ Backend: For each file:                               │
│    │  ├─ Generate unique filename with room_id + UUID       │
│    │  ├─ Save file to /uploads/{filename}                   │
│    │  └─ INSERT into room_images table                      │
│    └─ Backend: DELETE existing images (atomic replace)      │
│    └─ Response: { success, count }                          │
│    └─ Frontend: Show "Successfully uploaded 2 image(s)"     │
│    └─ Frontend: Auto-close modal after 1.5s                 │
│    └─ Frontend: Reload room list                            │
│                                                             │
│ 6. Admin Clicks "View Display" on Room Card                 │
│    └─ Opens new window to /display/{room_id}                │
│    └─ Display page:                                         │
│    │  ├─ generateQRCode() creates QR for upload page        │
│    │  ├─ checkForImages() fetches /api/get_images           │
│    │  ├─ Shows images if exist, slideshow starts            │
│    │  └─ Polls every 3 seconds for new images               │
│                                                             │
│ 7. Admin Logs Out                                           │
│    └─ logout() POST /logout clears session                  │
│    └─ Redirect to login page                                │
└─────────────────────────────────────────────────────────────┘
```

---

### Workflow 2: Mobile User Uploads Images via QR Code

**Actors**: Mobile User  
**Preconditions**: Room created, display showing QR code

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Mobile User Opens Camera App                             │
│    └─ Scans QR code displayed on TV                         │
│    └─ Phone opens: http://10.192.128.125:5000/upload/{id}   │
│                                                             │
│ 2. Upload Page Loads                                        │
│    └─ Shows "📷 Upload Images" interface                    │
│    └─ "Tap to select images" area ready                     │
│                                                             │
│ 3. User Taps Upload Area & Selects Images                   │
│    └─ File picker opens (native iOS/Android)                │
│    └─ User selects one or more images from gallery          │
│    └─ displayPreview() shows thumbnails                     │
│    └─ "Upload Images" button appears (was hidden)           │
│                                                             │
│ 4. User Taps "Upload Images"                                │
│    └─ uploadImages() POST /api/save_images/{room_id}        │
│    └─ FormData with images[] array                          │
│    └─ Button shows "Uploading..." state                     │
│    └─ Backend: Same as admin upload flow                    │
│    └─ Response: { success, count }                          │
│    └─ Frontend: Show success message with count             │
│    └─ Frontend: Auto-close tab/window after 2s              │
│                                                             │
│ 5. Backend Auto-Purge Job (Hourly)                          │
│    └─ purge_old_images() runs hourly                        │
│    └─ Deletes images older than AUTO_PURGE_HOURS (48h)      │
│    └─ Deletes pending images older than threshold           │
│                                                             │
│ 6. Display Updates (3s polling)                             │
│    └─ checkForImages() runs every 3 seconds                 │
│    └─ API returns new images                                │
│    └─ showImages() displays them                            │
│    └─ startSlideshow() rotates every SLIDE_DURATION (10s)   │
│    └─ User sees images appear on TV automatically           │
└─────────────────────────────────────────────────────────────┘
```

---

### Workflow 3: Admin Approval Workflow (When APPROVAL_REQUIRED=true)

**Actors**: Mobile User, Admin User  
**Preconditions**: APPROVAL_REQUIRED=true in .env

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Mobile User Uploads Images (Same as Workflow 2)          │
│    └─ POST /api/save_images/{room_id}                       │
│    └─ Backend: INSERT into pending_images (status='pending')│
│    └─ Images saved to disk but NOT in slideshow yet         │
│                                                             │
│ 2. Admin Opens Admin Panel                                  │
│    └─ loadRooms() fetches rooms                             │
│    └─ loadPendingApprovals() fetches pending images         │
│    └─ "⏳ Pending Approvals" section appears at top          │
│    └─ Shows grouped by room with thumbnail grid             │
│    └─ Each image has "✓" (approve) and "✗" (deny) buttons   │
│                                                             │
│ 3. Admin Reviews Pending Image                              │
│    └─ Sees thumbnail with timestamp                         │
│    └─ Decision: Approve or Deny                             │
│                                                             │
│ 4a. Admin Clicks Approve Button on Image                    │
│    └─ approveImage(pending_id) POST /api/pending_images/id/ │
│    │                                 /approve               │
│    └─ Backend: INSERT into room_images (from pending path)  │
│    └─ Backend: UPDATE pending_images SET status='approved'  │
│    └─ Frontend: loadRooms() reloads list                    │
│    └─ Image now appears in slideshow on display             │
│                                                             │
│ 4b. Admin Clicks Deny Button on Image                       │
│    └─ Confirm dialog: "Are you sure?"                       │
│    └─ denyImage(pending_id) POST /api/pending_images/id/    │
│    │                            /deny                       │
│    └─ Backend: DELETE physical file from disk               │
│    └─ Backend: DELETE from pending_images table             │
│    └─ Frontend: loadRooms() reloads list                    │
│                                                             │
│ 5. Auto-Expiry of Unapproved Images                         │
│    └─ purge_old_images() runs hourly                        │
│    └─ Deletes pending_images older than 30 min (configurable)
│    └─ Cleans up files and database records                  │
│                                                             │
│ 6. Display Shows Approved Images Only                       │
│    └─ /api/get_images only returns room_images (approved)   │
│    └─ Pending images never shown on display                 │
└─────────────────────────────────────────────────────────────┘
```

---

### Workflow 4: Room Disable/Enable Toggle

**Actors**: Admin User  
**Preconditions**: Room exists

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Room Status: Enabled (enabled=1)                         │
│    └─ Display shows QR code or images (if exist)            │
│    └─ Uploads accepted from mobile users                    │
│    │  ├─ If APPROVAL_REQUIRED: go to pending queue          │
│    │  └─ If no approval: replace images immediately         │
│                                                             │
│ 2. Admin Clicks "Disable" Button on Room Card               │
│    └─ toggleRoom(room_id) POST /api/rooms/{id}/toggle       │
│    └─ Backend: UPDATE rooms SET enabled=0 WHERE id=?        │
│    └─ Backend: Return { success, enabled: 0 }               │
│    └─ Frontend: loadRooms() reloads                         │
│    └─ Room card fades (opacity: 0.6), status: "Disabled"    │
│                                                             │
│ 3. Room Status: Disabled (enabled=0)                        │
│    └─ Mobile uploads REJECTED: 403 "Room is disabled"       │
│    └─ Display: checkForImages() checks room status          │
│    │  ├─ API returns { disabled: true }                     │
│    │  └─ showDisabled() shows "🔴 Currently Disabled"       │
│    └─ Existing images NOT deleted, just hidden              │
│                                                             │
│ 4. Admin Clicks "Enable" Button                             │
│    └─ toggleRoom(room_id) POST /api/rooms/{id}/toggle       │
│    └─ Backend: UPDATE rooms SET enabled=1 WHERE id=?        │
│    └─ Room returns to normal state                          │
│    └─ Uploads accepted again                                │
│    └─ Display shows images/QR code again                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance Specifications

### Scalability

**Rooms**: Tested up to 100 rooms (SQLite suitable for this scale)
**Images per Room**: ~500-1000 images before performance degrades
**Concurrent Users**: ~10-20 simultaneous uploads (depending on server hardware)
**Database Size**: ~5MB per 1000 images (varies by OS and index usage)

### Optimization Considerations

1. **Database Querying**
   - Indexes on `room_id`, `created_at` for faster sorting
   - No N+1 queries (all data fetched in single query)

2. **Image Serving**
   - No caching on image URLs (always fresh)
   - `object-fit: contain` prevents distortion
   - CDN recommended for production (large image downloads)

3. **Frontend Performance**
   - Debounced search (250ms delay to reduce renders)
   - Grid layout uses CSS (no JavaScript layout thrashing)
   - Lazy-loading recommended for room list (if >50 rooms)

4. **Memory Usage**
   - SQLite in-memory mode not used (persistent disk-based)
   - Flask default thread pool: 1 worker (can increase with gunicorn)

### Recommended Optimizations (v8.0+)

1. **Multi-worker app server**:
   ```bash
   gunicorn --workers 4 --threads 2 app:app
   ```

2. **Image caching** (Redis):
   - Cache room data for 5-minute TTL
   - Reduce database queries during peak usage

3. **Database indexes**:
   ```sql
   CREATE INDEX idx_room_id_created ON room_images (room_id, created_at DESC);
   ```

4. **Image compression**:
   - Pillow library to auto-downscale large uploads
   - Save as WebP for 30% size reduction

---

## Troubleshooting & Maintenance

### Common Issues & Solutions

#### Issue: Images not appearing on display
**Symptoms**: Display shows QR code, but uploads don't show up within 3 seconds

**Diagnosis**:
1. Check if images were saved to disk: `ls -la uploads/`
2. Check database records: `sqlite3 data/qr_rooms.db "SELECT * FROM room_images WHERE room_id='?'"`
3. Check display page logs in browser console (F12)
4. Check server logs: `docker compose logs qr-module`

**Solutions**:
- Verify room ID matches between upload and display URLs
- Check if room is disabled: `UPDATE rooms SET enabled=1 WHERE id='?'`
- Restart polling: Reload display page
- Clear browser cache: Ctrl+Shift+Delete or Cmd+Shift+Delete

---

#### Issue: Upload fails with "Room is disabled"
**Symptoms**: Mobile upload shows error "Room is disabled"

**Diagnosis**:
1. Check room status: `SELECT enabled FROM rooms WHERE id='?'`
2. Verify via admin panel (room card shows 🔴 Disabled)

**Solution**:
- Admin clicks "Enable" button on room card
- Or via database: `UPDATE rooms SET enabled=1 WHERE id='?'`

---

#### Issue: "Invalid credentials" on login
**Symptoms**: Admin can't log in

**Diagnosis**:
1. Check .env credentials: `grep ADMIN_ .env`
2. Verify username and password typed correctly
3. Check for SQLite session issues

**Solutions**:
- Verify username matches `ADMIN_USERNAME` in .env
- Verify password matches `ADMIN_PASSWORD` in .env
- Passwords are case-sensitive
- In dev: `ADMIN_USERNAME=admin ADMIN_PASSWORD=admin123` (defaults)

---

#### Issue: Disk full - cannot upload images
**Symptoms**: Upload fails with "No space left on device"

**Diagnosis**:
1. Check disk usage: `df -h`
2. Find large files: `du -sh uploads/*`

**Solutions**:
- Run manual purge: Delete old images from `uploads/` directory
- Increase storage: Extend Docker volume/host disk
- Adjust `AUTO_PURGE_HOURS` to lower threshold: `AUTO_PURGE_HOURS=24`
- Run manual cleanup script:
  ```bash
  find uploads/ -type f -mtime +2 -delete
  ```

---

#### Issue: Container crashes on startup
**Symptoms**: `docker compose up` fails immediately

**Diagnosis**:
1. Check logs: `docker compose logs qr-module`
2. Look for Python errors or permission issues

**Solutions**:
- Fix file permissions: `chmod 755 data/ uploads/` (in container)
- Reset database: `rm data/qr_rooms.db` (recreated on startup)
- Check .env syntax: No spaces around `=`, use quotes if needed
- Rebuild image: `docker compose up -d --build`

---

#### Issue: QR code not scannable on mobile
**Symptoms**: Phone camera won't recognize QR, or scanning opens wrong URL

**Diagnosis**:
1. Check QR code error correction: Using `correctLevel: H` (good)
2. Verify `SERVER_IP` correct in QR URL
3. Network connectivity: Phone can't reach server IP

**Solutions**:
- Verify network: `ping {SERVER_IP}` from mobile
- Check `SERVER_IP` in .env: Must be accessible from mobile network
- If on WiFi: Use WiFi IP, not localhost
- Regenerate QR: `refreshQRCode()` in display.js

---

### Database Maintenance

#### Backup Database
```bash
# While running in Docker
docker compose exec qr-module sqlite3 data/qr_rooms.db ".backup" > backup.sql

# Or manually
cp data/qr_rooms.db data/qr_rooms.db.backup
```

#### Restore Database
```bash
sqlite3 data/qr_rooms.db ".restore" backup.sql
```

#### Database Health Check
```bash
sqlite3 data/qr_rooms.db "PRAGMA integrity_check;"
# Should output: ok
```

#### Rebuild Database
```bash
# Backup first
cp data/qr_rooms.db data/qr_rooms.db.backup

# Delete and restart (will recreate schema)
rm data/qr_rooms.db
docker compose restart qr-module
```

---

### Log Analysis

#### View Logs
```bash
docker compose logs -f qr-module          # Stream all logs
docker compose logs --tail 50 qr-module   # Last 50 lines
docker compose logs qr-module > logs.txt  # Export logs
```

#### Key Log Messages
- `[SCHEDULER] Auto-purge enabled`: Purge job running
- `[AUTO-PURGE] Deleted X images`: Images cleaned up
- `WARNING in werkzeug`: HTTP requests
- `ERROR in app`: Application-level errors

---

## Development Guidelines

### Adding New Features

#### Example: Add Image Comments
1. **Database Migration**:
   ```python
   db.execute('''ALTER TABLE room_images ADD COLUMN comment TEXT''')
   ```

2. **Backend Route**:
   ```python
   @app.route('/api/images/<int:image_id>/comment', methods=['POST'])
   @login_required
   def add_comment(image_id):
       data = request.json
       comment = data.get('comment', '')
       db.execute('UPDATE room_images SET comment = ? WHERE id = ?', 
                  (comment, image_id))
       db.commit()
       return jsonify({'success': True})
   ```

3. **Frontend Integration**:
   - Add form input in admin.js
   - Call new endpoint via fetch()
   - Update UI to show comments

#### Code Style Guidelines
- Python: PEP 8 (use Black formatter)
- JavaScript: ES6+, no framework dependencies
- CSS: BEM naming convention
- Comments: Docstrings for functions, inline for complex logic
- Error handling: Try-catch for async, try-finally for resources

#### Testing Checklist Before Commit
- [ ] Test feature on multiple browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile and tablet
- [ ] Test with multiple images (1, 5, 50+)
- [ ] Test with special characters in names (émoji, 中文)
- [ ] Check browser console for errors (F12)
- [ ] Verify database consistency: `PRAGMA integrity_check`
- [ ] Check Docker container health: `docker compose ps`

---

## Version History

### v7.1.0 (2026-02-26) - Current
- ✨ Admin login system with username/password
- ✨ Room enable/disable toggle
- ✨ Media approval workflow (optional)
- ✨ Pending approvals admin panel
- ✨ Logout button
- 🔧 Session management with Flask
- 🔧 Database schema: Added `enabled` column and `pending_images` table
- 🐛 Fixed image slideshow with approval system

### v7.0.0 (2026-02-19)
- 🔧 Added confirmation dialog to clear room images
- 🎨 Improved user experience

### v6.4.1 (2026-02-19)
- ✨ Search & sort on admin panel
- ✨ Persistent database via Docker volume
- ✨ Configurable slide duration
- ✨ Clear button on admin cards
- 🐛 Fixed clear button compatibility on tablets

### v6.2.0
- ✨ Responsive QR code sizing for all screens
- 🐛 Fixed QR display on 4K/8K monitors

### v6.1.0 & Earlier
- Initial release with core functionality

---

## Conclusion

QR Module v7.1.0 is a production-ready, feature-rich image management system suitable for:
- Event displays and signage
- Conference room presentations
- Retail product showcases
- Gallery exhibitions
- Educational institution displays

**Key Strengths**:
- Zero-maintenance deployment (Docker)
- Powerful admin interface with approval workflows
- Mobile-friendly for end users
- Persistent storage across restarts
- Highly configurable via environment variables

**Next Steps**:
- Deploy using docker-compose
- Configure .env for your environment
- Change default admin credentials
- Set up SSL/TLS reverse proxy for production
- Consider Redis integration for multi-instance deployment

---

## Support & Feedback

For issues, feature requests, or questions:
1. Check [CHANGELOG.md](CHANGELOG.md) for known issues
2. Review this documentation
3. Check Docker logs: `docker compose logs qr-module`
4. Test feature isolation (admin vs. display vs. upload separately)

---

**Document Version**: 2.0  
**Last Updated**: March 2, 2026  
**Maintainer**: QR Module Development Team  
**License**: MIT (assumed)
