# QR Module v7.1.0 - Complete Deployment & Operations Guide

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Capabilities](#capabilities)
4. [Architecture & Components](#architecture--components)
5. [Admin Workflow](#admin-workflow)
6. [User (Display) Workflow](#user-display-workflow)
7. [Deployment Procedures](#deployment-procedures)
8. [Security Considerations for Hospital Environments](#security-considerations-for-hospital-environments)
9. [Troubleshooting](#troubleshooting)
10. [Support & Maintenance](#support--maintenance)

---

## Executive Summary

**QR Module v7.1.0** is a multi-room image management system designed for TV/monitor displays in healthcare and enterprise environments. Users scan QR codes with mobile devices to upload images to designated rooms, which are then automatically displayed as rotating slideshows on wall-mounted monitors or TVs.

**Key Use Cases:**
- Hospital patient room displays (X-rays, imaging, data visualization)
- Educational room displays (presentations, diagrams, study materials)
- Emergency department information screens
- Waiting room digital signage
- Conference room displays

**Current Version:** 7.1.0  
**Release Date:** February 26, 2026  
**License:** Internal Use  
**Last Updated:** February 26, 2026

---

## System Overview

### What Problems Does It Solve?
1. **No wireless/physical connection required** - Users scan QR code on their phone; no cable, USB, or WiFi setup needed
2. **Multiple rooms in one system** - Manage unlimited displays from single admin panel
3. **Real-time updates** - Images appear on displays within seconds
4. **Content control** - Optional admin approval prevents inappropriate content
5. **Temporary displays** - Images auto-delete after configurable time without manual cleanup
6. **Admin security** - Login required; role-based access control

### Who Uses It?
- **Administrators:** Set up rooms, manage content, approve uploads, monitor system
- **End Users:** Scan QR code with phone, select image, tap upload
- **Display Nodes:** TV/monitor displays pull image feed from server

---

## Capabilities

### ✅ Core Features

| Feature | Description | Hospital Relevance |
|---------|-------------|-------------------|
| **Multi-Room Support** | Create unlimited rooms with unique QR codes | Different departments/floors |
| **QR Code Upload** | Scan with phone to upload via web interface | No IT setup required - user-friendly |
| **Admin Upload** | Upload directly from admin panel | Rapid deployment, testing |
| **Auto-Slideshow** | Rotate images on display every N seconds | Continuous information flow |
| **Admin Approval** | Optional pre-approval for all uploads | Compliance, content control |
| **Room Enable/Disable** | Toggle rooms on/off without deletion | Maintenance, testing |
| **Search & Sort** | Filter/organize rooms by name, status, date | Easy management |
| **Persistent Storage** | Images survive system restart | Data retention |
| **Session Management** | User authentication with configurable credentials | Access control |
| **Auto-Purge** | Old images automatically delete after N hours | Storage management |

### 🔒 Security Features

| Feature | Description |
|---------|-------------|
| **Admin Login** | Username/password protected admin panel |
| **Session Tokens** | Server-side session management |
| **Content Approval** | Optional workflow for upload validation |
| **File Isolation** | Images stored with room + unique identifiers |
| **HTTPS Ready** | Can deploy behind SSL/TLS proxy |
| **Access Control** | Admin endpoints require authentication |

### 📊 Data Management

| Capability | Default | Configurable |
|-----------|---------|--------------|
| Max File Size | 50 MB | Via Flask config |
| Image Retention | 48 hours | `AUTO_PURGE_HOURS` |
| Slideshow Duration | 5 seconds | `SLIDE_DURATION` |
| Approval Expiry | 30 minutes | `PENDING_IMAGE_EXPIRY_MINUTES` |
| Polling Interval | 3 seconds | Hardcoded in JS |

---

## Architecture & Components

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    HOSPITAL NETWORK                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────────────┐   │
│  │  Mobile Phones   │         │  QR Module Server        │   │
│  │  (User Upload)   │         │  (Flask + SQLite)        │   │
│  │                  │         │                          │   │
│  │  - Scan QR       │◄───────►│  - REST API              │   │
│  │  - Select Image  │ HTTPS   │  - Authentication        │   │
│  │  - Upload to     │         │  - Image Storage         │   │
│  │    Room          │         │  - Approval Workflow     │   │
│  └──────────────────┘         │  - Session Management    │   │
│                                │  - Schedule Purge        │   │
│  ┌──────────────────┐         │                          │   │
│  │ Admin Browser    │         └──────────────────────────┘   │
│  │ (Chrome/Safari)  │                      ↕                  │
│  │                  │         ┌──────────────────────────┐   │
│  │ - Login          │◄───────►│  SQLite Database         │   │
│  │ - Room CRUD      │ HTTPS   │  - Rooms table           │   │
│  │ - Manage Content │         │  - Images table          │   │
│  │ - Approve/Deny   │         │  - Pending Images table  │   │
│  │ - View Analytics │         │  - 📁 /data/qr_rooms.db │   │
│  └──────────────────┘         └──────────────────────────┘   │
│                                                               │
│  ┌──────────────────┐         ┌──────────────────────────┐   │
│  │ Display Devices  │         │  File Storage            │   │
│  │ (TV/Monitor)     │         │                          │   │
│  │                  │         │  📁 /uploads/            │   │
│  │ - Pull Images    │◄───────►│  - room_uuid_*.jpg       │   │
│  │ - Slideshow      │ HTTP    │  - room_uuid_*.png       │   │
│  │ - Full Screen    │         │                          │   │
│  └──────────────────┘         └──────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### **Backend (Python/Flask)**
**File:** `app.py` (415 lines)

**Responsibilities:**
- HTTP request handling (routing)
- Database operations (SQLite)
- File upload processing
- Session management
- Scheduled tasks (auto-purge)
- REST API endpoints

**Key Dependencies:**
```
Flask==2.3.3              # Web framework
Flask-CORS==4.0.0         # Cross-origin requests
Werkzeug==2.3.7           # WSGI utilities
APScheduler==3.10.4       # Background jobs
python-dotenv==1.0.0      # Environment config
```

#### **Frontend - Admin Panel**
**Files:** 
- `templates/admin.html` (54 lines)
- `static/js/admin.js` (430+ lines)
- `static/css/admin.css` (380+ lines)

**Features:**
- Room creation/deletion
- Image batch upload
- Room enable/disable toggle
- Content search & sorting
- Pending approval management
- Logout functionality

#### **Frontend - Display Page**
**Files:**
- `templates/display.html` (26 lines)
- `static/js/display.js` (150+ lines)
- `static/css/display.css` (120+ lines)

**Features:**
- QR code generation
- Image polling (every 3 seconds)
- Automatic slideshow rotation
- Full-screen display mode
- Disabled room message
- Clear all button (for operators)

#### **Frontend - Login Page**
**Files:**
- `templates/login.html` (80 lines)
- `static/css/login.css` (114 lines)

**Features:**
- Username/password form
- Session persistence
- Error messaging
- Mobile-friendly design

#### **Database (SQLite)**
**Location:** `data/qr_rooms.db`

**Schema:**
```sql
-- Rooms (one per logical display)
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,              -- UUID (first 8 chars)
    name TEXT NOT NULL,               -- Display name
    enabled INTEGER DEFAULT 1,        -- 0=disabled, 1=enabled
    created_at TIMESTAMP              -- Creation time
);

-- Room Images (approved content)
CREATE TABLE room_images (
    id INTEGER PRIMARY KEY,           -- Auto-increment
    room_id TEXT NOT NULL,            -- Foreign key to rooms
    image_path TEXT NOT NULL,         -- File path on disk
    uploaded_at TIMESTAMP,            -- Upload time
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

-- Pending Images (awaiting approval)
CREATE TABLE pending_images (
    id INTEGER PRIMARY KEY,           -- Auto-increment
    room_id TEXT NOT NULL,            -- Foreign key to rooms
    image_path TEXT NOT NULL,         -- File path on disk
    uploaded_at TIMESTAMP,            -- Upload time
    status TEXT DEFAULT 'pending',    -- 'pending', 'approved', 'denied'
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);
```

#### **Configuration (.env)**
**Location:** `.env` (root directory)

```bash
# Network Configuration
SERVER_IP=192.168.1.197        # Server LAN IP (or external IP)
SERVER_PORT=5000               # Flask port

# Image Management
AUTO_PURGE_ENABLED=true        # Auto-delete old images
AUTO_PURGE_HOURS=48            # Delete images older than N hours
SLIDE_DURATION=5000            # Slideshow interval (ms)

# Admin Authentication
ADMIN_USERNAME=admin           # Login username
ADMIN_PASSWORD=admin123        # Login password
SECRET_KEY=auto-generated      # Session encryption (auto if blank)

# Content Approval System
APPROVAL_REQUIRED=false        # Require admin approval for uploads
PENDING_IMAGE_EXPIRY_MINUTES=30 # Auto-delete unapproved uploads
```

---

## Admin Workflow

### Step 1: Access Admin Panel

```
1. Open browser: http://SERVER_IP:5000/
2. You will be redirected to login page
3. Enter credentials:
   - Username: (from .env ADMIN_USERNAME)
   - Password: (from .env ADMIN_PASSWORD)
4. Click "Login"
```

### Step 2: Create a Room

```
On Admin Dashboard:
┌─────────────────────────────┐
│ Enter room name (e.g., ER1) │
│ Click "Create Room"         │
└─────────────────────────────┘

Behind the scenes:
- Server generates unique ID (8-char UUID)
- Database creates new room record
- QR code becomes: http://SERVER_IP:5000/display/ROOM_ID
- Room appears in grid below
```

### Step 3: View Room

```
For each room card:
┌─────────────────────────────┐
│ Room Name: ER1              │
│ Room ID: a1b2c3d4          │
│ Status: 🟢 Enabled         │
│ URL: http://...display/... │
├─────────────────────────────┤
│ Buttons:                    │
│ [View] [Upload] [Toggle]   │
│ [Clear] [Delete]           │
└─────────────────────────────┘

- "View": Opens display in new tab (shows QR or slideshow)
- "Upload": Opens file picker modal
- "Toggle": Enable/disable room
- "Clear": Remove all images from room
- "Delete": Remove room entirely
```

### Step 4: Upload Images (Admin)

```
Option A - Direct Upload:
┌─────────────────────────────┐
│ Click "Upload Images"       │
│ Select 1+ files            │
│ Preview shows thumbnails   │
│ Click "Upload Images"      │
│ Status: "Successfully      │
│  uploaded 3 image(s)"      │
└─────────────────────────────┘

Option B - User Uploads via QR:
- Users scan room QR code with phone
- Select image from phone camera roll
- Image appears in pending queue (if approval enabled)
```

### Step 5: Approve Pending Content (if enabled)

```
If APPROVAL_REQUIRED=true:

⏳ PENDING APPROVALS
├─ ER1 [3 pending]
│  ┌──┐ ┌──┐ ┌──┐
│  │1 │ │2 │ │3 │  ← Thumbnail previews
│  │✓ │ │✓ │ │✓ │  ← Approve/Deny buttons
│  └──┘ └──┘ └──┘
│
└─ ER2 [1 pending]
   ┌──┐
   │1 │
   │✓ │
   └──┘

Click ✓ to approve → image moves to slideshow
Click ✗ to deny   → image deleted
```

### Step 6: Manage Room State

```
Toggle Enable/Disable:
┌─────────────────────────────┐
│ Room Name: ER1              │
│ Status: 🟢 Enabled          │
│ [Disable]                   │
└─────────────────────────────┘

After disable:
- Room card faded/greyed
- Display shows "🔴 Currently Disabled"
- QR scan still works but shows disabled message
- Can click [Enable] to reactivate

Use Case: Maintenance, testing, temporary closure
```

### Step 7: Search & Sort

```
SEARCH:
┌──────────────────────┐
│ Search ER [✕]       │  ← Type to filter rooms
└──────────────────────┘

SORT:
[Newest] [Oldest] [A-Z] [Z-A] [Enabled First]
   ↕        ↕      ↕      ↕        ↕

Results: "3 results"  ← Shows matching count
```

### Step 8: Logout

```
┌─────────────────────────────┐
│ QR Module - Room Management │
│              [Logout] ←────── in header
└─────────────────────────────┘

- Clears session
- Redirects to login page
- Next access requires re-authentication
```

---

## User (Display) Workflow

### For End Users (Phone Upload)

```
STEP 1: USER SCANS QR
┌──────────────┐
│ User holds   │
│ phone to     │
│ room display │
└──────────────┘
       ↓
    Phone camera app detects QR code
       ↓
    Opens: http://SERVER_IP:5000/upload/ROOM_ID
       ↓

STEP 2: UPLOAD INTERFACE
┌─────────────────────────────────┐
│ 📱 Upload to: [Room Name]       │
├─────────────────────────────────┤
│ Take Photo    │ Choose from     │
│ (camera)      │ Camera Roll     │
└─────────────────────────────────┘
       ↓
    User selects image
       ↓

STEP 3: PREVIEW & SEND
┌─────────────────────────────────┐
│ 🖼️ [Image Preview]              │
├─────────────────────────────────┤
│ [Upload]  [Cancel]              │
└─────────────────────────────────┘
       ↓
    Click upload
       ↓

STEP 4: CONFIRMATION
┌─────────────────────────────────┐
│ ✓ Image uploaded successfully   │
│   (appears on room display      │
│    in 1-3 seconds)              │
└─────────────────────────────────┘

OR (if approval required):
┌─────────────────────────────────┐
│ ⏳ Image sent for approval      │
│    (admin will review)          │
└─────────────────────────────────┘
```

### For Display Devices (Monitor/TV)

```
STEP 1: DISPLAY PAGE LOADS
URL: http://SERVER_IP:5000/display/ROOM_ID
       ↓
    Page loads browser in full-screen mode
       ↓

STEP 2: CHECKS FOR IMAGES
Every 3 seconds:
├─ If images exist AND room enabled:
│  └─ Show slideshow (rotate every 5s)
│
├─ If no images:
│  └─ Show QR code (display this QR on screen)
│
└─ If room is disabled:
   └─ Show "🔴 Currently Disabled"

STEP 3: SLIDESHOW
┌─────────────────────────────┐
│ Image 1                     │
│ (5 seconds)                 │
└─────────────────────────────┘
       ↓ (auto rotate)
┌─────────────────────────────┐
│ Image 2                     │
│ (5 seconds)                 │
└─────────────────────────────┘
       ↓ (auto rotate)
┌─────────────────────────────┐
│ Image 1 (loop back)         │
└─────────────────────────────┘

STEP 4: CLEARING IMAGES
[Clear] button (bottom right)
- Removes all images from room
- Reverts to QR code view
- Useful if wrong content uploaded

NOTE: Display constantly polls server
      even if images not changing.
      Server always returns latest.
```

---

## Deployment Procedures

### Pre-Deployment Checklist

- [ ] Server hardware identified (laptop, Raspberry Pi, or dedicated VM)
- [ ] Server IP address determined and static (DHCP reservation recommended)
- [ ] Network access confirmed (server can reach WiFi or wired network)
- [ ] Port 5000 open on firewall/router (or reverse proxy configured)
- [ ] Python 3.8+ installed (if direct deployment)
- [ ] Docker installed (if containerized deployment)
- [ ] SSL/TLS certificate obtained (if HTTPS required)
- [ ] Hospital network policies reviewed
- [ ] Data retention requirements confirmed
- [ ] Approval workflow needs identified

### Option 1: Docker Deployment (Recommended)

**Advantages:**
- Isolated environment
- Easier to manage multiple versions
- Consistent across machines
- Built-in networking

**Prerequisites:**
```powershell
# Install Docker Desktop from: https://www.docker.com/products/docker-desktop
# Verify installation:
docker --version
docker compose --version
```

**Deployment Steps:**

```powershell
# 1. Clone or pull repository
git clone https://github.com/davidgorley/qr-module.git
cd qr-module
# OR if already cloned:
git pull origin main

# 2. Configure environment
# Edit .env file with hospital settings
notepad .env
# Key settings:
#   SERVER_IP=192.168.1.100  (hospital network IP)
#   ADMIN_USERNAME=hospitaladmin
#   ADMIN_PASSWORD=StrongPassword123!
#   APPROVAL_REQUIRED=true    (for compliance)

# 3. Build Docker image
docker compose build

# 4. Start containers
docker compose up -d

# 5. Verify running
docker compose ps
# Should show:
# qr-module   Up 2 seconds   0.0.0.0:5000->5000/tcp

# 6. Test accessibility
# Open browser: http://localhost:5000
# Should redirect to login page

# 7. View logs if needed
docker compose logs -f
# Press Ctrl+C to exit logs
```

**Stopping/Restarting:**

```powershell
# Stop containers
docker compose down

# Restart
docker compose up -d

# Remove everything (use with caution in production)
docker compose down -v  # -v removes volumes (database!)
```

### Option 2: Direct Python Deployment

**Prerequisites:**
```powershell
# Install Python 3.8+: https://www.python.org/downloads/

# Verify:
python --version

# Install pip (usually bundled)
pip --version
```

**Deployment Steps:**

```powershell
# 1. Clone or pull repository
git clone https://github.com/davidgorley/qr-module.git
cd qr-module
# OR:
git pull origin main

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
# Create/edit .env file
notepad .env
# Add settings (see Option 1)

# 6. Create data directory
mkdir data

# 7. Run application
python app.py

# Server should start:
# WARNING in app.py (line XXX): CORS is enabled
# [SCHEDULER] Auto-purge enabled: every 1 hour
# Running on http://0.0.0.0:5000
```

**Stopping/Restarting:**

```powershell
# Stop: Press Ctrl+C in terminal
# Deactivate venv:
deactivate
# Restart:
.\venv\Scripts\activate
python app.py
```

### Option 3: Raspberry Pi Deployment

**Hardware:**
- Raspberry Pi 4 (2GB+ RAM recommended)
- MicroSD card (32GB+)
- Power supply
- Ethernet cable or WiFi dongle

**Deployment Steps:**

```bash
# 1. Install Raspberry Pi OS (Lite or Desktop)
# Download from: https://www.raspberrypi.com/software/

# 2. Boot Pi and connect to internet

# 3. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 4. Install dependencies
sudo apt-get install -y python3 python3-pip git

# 5. Clone repository
git clone https://github.com/davidgorley/qr-module.git
cd qr-module

# 6. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 7. Install Python packages
pip install -r requirements.txt

# 8. Configure .env
nano .env
# Set SERVER_IP to Pi's IP (use: hostname -I)

# 9. Run application
python3 app.py

# 10. Optional: Auto-start on boot
# Create systemd service:
sudo nano /etc/systemd/system/qr-module.service

# Add content:
[Unit]
Description=QR Module Flask App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/qr-module
Environment="PATH=/home/pi/qr-module/venv/bin"
ExecStart=/home/pi/qr-module/venv/bin/python app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable service:
sudo systemctl enable qr-module
sudo systemctl start qr-module

# Check status:
sudo systemctl status qr-module
```

### Option 4: Cloud Deployment (AWS/Azure/GCP)

**For hospital-grade deployment:**

1. **Launch VM instance** (Ubuntu 20.04 LTS)
2. **Configure security groups** (allow ports 80, 443)
3. **Install software** (Python, Docker, Nginx)
4. **Deploy application** (via Docker)
5. **Configure SSL** (Let's Encrypt + Nginx reverse proxy)
6. **Setup monitoring** (CloudWatch/Azure Monitor)
7. **Configure backups** (automated DB snapshots)

**Example Nginx reverse proxy config:**

```nginx
server {
    listen 443 ssl http2;
    server_name qr-module.hospital.org;

    ssl_certificate /etc/letsencrypt/live/qr-module.hospital.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/qr-module.hospital.org/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name qr-module.hospital.org;
    return 301 https://$server_name$request_uri;
}
```

---

## Security Considerations for Hospital Environments

### 1. Authentication & Access Control

#### Current Implementation
- ✅ Admin login with username/password
- ✅ Session management with server-side tokens
- ! Single admin account (all admins share credentials)

#### Hospital Best Practices

**CRITICAL - Before Deployment:**

```python
# NEVER use default credentials!
# Set in .env:
ADMIN_USERNAME=your-hospital-specific-username  # NOT "admin"
ADMIN_PASSWORD=StrongP@ssw0rd!2026               # min 12 chars

# Recommended password policy:
# - Minimum 12 characters
# - Mix of uppercase, lowercase, numbers, symbols
# - No common hospital acronyms or dates
# - Changed every 90 days
```

**Risk: Weak Credentials**
- Default "admin/admin123" allows unauthorized access
- Credentials in `.env` visible to anyone with server access

**Mitigation:**
- ✅ Use strong, unique credentials
- ✅ Store `.env` file with restricted permissions (600)
- ✅ Use environment variables from secure vault (not file)
- ✅ Implement IP whitelisting at firewall level
- ✅ Rotate credentials quarterly
- ✅ Audit login attempts (enhancement in future)

#### Enhancement: Multi-User Support (Future)

Recommended implementation:
```python
# Add to database schema:
CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,  # bcrypt hashed
    department TEXT,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);

# Track approval actions:
CREATE TABLE approval_audit (
    id INTEGER PRIMARY KEY,
    admin_id INTEGER,
    pending_id INTEGER,
    action TEXT,  # 'approved' or 'denied'
    reason TEXT,
    timestamp TIMESTAMP
);
```

### 2. Data Privacy & HIPAA Compliance

#### Current Implementation
- ✅ Images stored with room scoping (cannot access other rooms)
- ✅ No patient identifiers stored in database
- ! No encryption at rest
- ! No encryption in transit (HTTP only)

#### Hospital Requirements

**CRITICAL COMPLIANCE ISSUES:**

| Issue | Current | Hospital Need | Solution |
|-------|---------|---------------|----------|
| **Encryption in Transit** | HTTP (plain text) | HTTPS (encrypted) | Deploy behind SSL proxy |
| **Encryption at Rest** | Plain files on disk | Encrypted storage | EFS encryption or FileVault |
| **Access Logs** | File creation only | Complete audit trail | Enhanced logging |
| **Data Retention** | 48 hours default | Customizable per policy | Already configurable |
| **Patient Data** | N/A | Prohibited in uploads | Add content warnings |

**Deployment with HTTPS (Required):**

```bash
# Using Nginx + Let's Encrypt (free SSL)

# 1. Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# 2. Generate certificate
sudo certbot certonly --standalone -d your-hospital-domain.org

# 3. Configure Nginx (see config above)

# 4. Test SSL
curl https://your-hospital-domain.org/

# 5. Auto-renew
sudo systemctl enable certbot.timer
```

**Encryption at Rest:**

```bash
# Option A: Filesystem-level (Linux)
# Use encrypted partition for /data/
sudo cryptsetup luksFormat /dev/sdX
sudo cryptsetup luksOpen /dev/sdX data
sudo mkfs.ext4 /dev/mapper/data

# Option B: Container secrets (Docker)
# Store sensitive data in Docker secrets (production)

# Option C: Cloud-native (AWS/Azure)
# Use EFS encryption or managed database
```

### 3. Network Security

#### Current Implementation
- ✅ CORS enabled for local network
- ✅ No external dependencies
- ! No rate limiting
- ! No DDoS protection

#### Hospital Requirements

**Firewall Configuration:**

```
INBOUND RULES:
- Port 443: HTTPS (from hospital WiFi/LAN only)
- Port 5000: Application (internal only, NOT exposed to internet)
- Port 22: SSH (admin only, with key-based auth)

OUTBOUND RULES:
- Block all internet access (no external phone homes)
- Allow internal NTP (time sync)
- Allow internal DNS

NETWORK SEGMENTS:
- Place server on isolated hospital network segment
- Do NOT expose directly to guest WiFi
- Restrict to staff VLAN
```

**Rate Limiting (Enhancement):**

```python
# Add to app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent brute force
def login():
    # ... implementation
    pass
```

### 4. File Upload Security

#### Current Implementation
- ✅ File extension check (images only)
- ✅ 50 MB file size limit
- ! No MIME type validation
- ! No virus scanning
- ! Files directly served

#### Hospital Requirements

**Enhanced File Handling:**

```python
import magic
import mimetypes

ALLOWED_MIMETYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
BLOCKED_EXTENSIONS = {'.exe', '.bat', '.cmd', '.scr', '.vbs', '.js'}

def validate_upload(file):
    # 1. Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext in BLOCKED_EXTENSIONS:
        return False, "File type not allowed"
    
    # 2. Check MIME type (using file magic)
    mime = magic.from_buffer(file.stream.read(1024), mime=True)
    if mime not in ALLOWED_MIMETYPES:
        return False, "Invalid file type"
    
    # 3. Scan with ClamAV (virus scanner)
    if not scan_with_clamav(file.stream):
        return False, "File flagged as suspicious"
    
    return True, "OK"

# In save_images endpoint:
is_valid, message = validate_upload(file)
if not is_valid:
    return jsonify({'success': False, 'error': message}), 400
```

**Virus Scanning Integration:**

```bash
# Install ClamAV
sudo apt-get install clamav clamav-daemon

# Configure in Python
import pyclamd

clam = pyclamd.ClamD()

if not clam.is_running():
    clam.reload()

# Scan uploaded file
scan_result = clam.scan_file(filepath)
if scan_result:
    # File flagged, log and delete
    os.remove(filepath)
    log_security_incident(filepath, scan_result)
```

### 5. Database Security

#### Current Implementation
- ✅ SQLite (no network access)
- ✅ File-based (easier to backup)
- ! No encryption
- ! No access control (file-level only)

#### Hospital Requirements

**Database Protection:**

```bash
# 1. File permissions
chmod 600 /data/qr_rooms.db
sudo chown qr-module:qr-module /data/qr_rooms.db

# 2. Backup strategy
# Daily encrypted backups to hospital storage
0 2 * * * /backup/backup-qr-module.sh

# backup-qr-module.sh:
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
openssl enc -aes-256-cbc -salt -in /data/qr_rooms.db \
    -out /backup/qr_rooms_$TIMESTAMP.db.enc \
    -k $BACKUP_PASSWORD
```

**Audit Logging:**

```python
# Log database modifications
import logging

db_logger = logging.getLogger('database')
handler = logging.FileHandler('/var/log/qr-module/database.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
db_logger.addHandler(handler)

# In approve_image endpoint:
db_logger.info(f"APPROVE: user={session.user}, image_id={pending_id}, room_id={room_id}")

# In deny_image endpoint:
db_logger.info(f"DENY: user={session.user}, image_id={pending_id}, room_id={room_id}")
```

### 6. Incident Response

#### Breach Scenario: Unauthorized Access

```
1. Detect: Admin notices unfamiliar images in room
2. Investigate:
   - Check access logs: tail -f /var/log/qr-module/access.log
   - Query database: SELECT * FROM approval_audit ORDER BY timestamp DESC
   - Review firewall logs for suspicious IPs
3. Contain:
   - Disable affected room: UPDATE rooms SET enabled=0 WHERE id='X'
   - Change admin credentials immediately
   - Kill all sessions: DELETE FROM sessions
4. Eradicate:
   - Clear pending uploads: DELETE FROM pending_images
   - Clear room images: DELETE FROM room_images WHERE room_id='X'
   - Reboot server
5. Recover:
   - Restore from backup (pre-breach)
   - Re-enable room with clean slate
6. Learn:
   - Add access control (IP whitelist)
   - Increase monitoring frequency
   - Document incident
```

#### Breach Scenario: Data Exfiltration

```
1. Monitor: Watch for unusual network traffic
   - Enable server monitoring (bandwidth, connections)
   - Alert on egress to public IPs
2. Prevent:
   - Firewall: block all outbound except approved destinations
   - No external APIs or phone homes
   - Isolated network segment
3. If breach occurs:
   - Immediate network isolation
   - Forensic capture of logs
   - Incident report to compliance officer
```

### 7. Compliance Checklist

**Before Hospital Deployment:**

- [ ] Security assessment completed
- [ ] HIPAA risk analysis (if handling PHI)
- [ ] Penetration testing performed
- [ ] SSL/TLS certificate deployed
- [ ] Firewall rules configured
- [ ] Access controls implemented
- [ ] Incident response plan documented
- [ ] Backup/disaster recovery tested
- [ ] Audit logging enabled
- [ ] Staff training completed
- [ ] Policies documented (acceptable use, data retention)
- [ ] Legal review completed
- [ ] Insurance updated
- [ ] Compliance officer signoff

### 8. Monitoring & Alerting

**Recommended Alerts:**

```python
# 1. Login failures
def log_failed_login(username):
    alert_if(count_failed_logins(username, hours=1) > 5,
             "Multiple login failures", "SECURITY")

# 2. Unusual upload volumes
def check_upload_volume():
    recent = count_uploads(hours=1)
    alert_if(recent > 1000, "Unusual upload volume", "WARNING")

# 3. Server health
def check_disk_space():
    used = get_disk_usage()
    alert_if(used > 90, "Disk space low", "WARNING")

# 4. Database size (potential DoS)
def check_database_size():
    size = get_database_size()
    alert_if(size > 10_GB, "Database unusually large", "WARNING")
```

**Monitoring Tools:**

```bash
# Option 1: Prometheus + Grafana (cloud-native)
# Option 2: Nagios/Icinga (hospital standard)
# Option 3: Datadog/New Relic (managed monitoring)
# Option 4: ELK Stack (Elasticsearch/Logstash/Kibana)

# Simple approach: cron job + email alerts
*/30 * * * * /monitoring/check-qr-module.sh
```

---

## Troubleshooting

### Issue: Cannot Connect to Server

**Symptoms:** Login page won't load, "Connection refused" or "timeout"

**Diagnosis:**

```powershell
# 1. Verify server is running
docker compose ps
# OR
ps aux | grep python

# 2. Check if port is listening
netstat -an | grep 5000
# Should show: LISTENING or ESTABLISHED

# 3. Verify firewall allows port 5000
# Windows:
netsh advfirewall firewall show rule name=all | grep 5000

# 4. Test connectivity from another machine
curl http://SERVER_IP:5000/
# Should return HTML (login page)

# 5. Check server logs for errors
docker compose logs -f app
# OR
tail -f .log (if direct Python)
```

**Solutions:**

```powershell
# If port in use:
netstat -ano | grep 5000
taskkill /PID <PID> /F
# Then restart

# If firewall blocking:
# Windows Defender: Settings > Firewall > Allow app
# Router: Port forwarding (if external access needed)

# If server not running:
# Docker:
docker compose up -d --build

# Python:
.\venv\Scripts\activate
python app.py
```

### Issue: Images Don't Appear on Display

**Symptoms:** Upload succeeds but display still shows QR code

**Diagnosis:**

```powershell
# 1. Verify images saved
dir uploads/
# Should show files like: room_id_uuid_filename.jpg

# 2. Check database
# Login to admin, verify image count in room

# 3. Check display polling
# Open browser developer tools (F12)
# Network tab: look for /api/get_images/{room_id}
# Should return 200 with image URLs

# 4. Check room enabled status
# Admin panel: verify room not disabled (grayed out)

# 5. Check JavaScript console for errors
# Press F12, Console tab, look for red errors
```

**Solutions:**

```bash
# If images not in database:
# Check app.py save_images endpoint
docker compose logs app | grep save_images

# If polling not working:
# Check if display URL correct: http://SERVER_IP:5000/display/ROOM_ID
# Verify room_id matches

# If room disabled:
# Admin panel: click "Enable"

# If file permission issue:
chmod 755 uploads/
chmod 644 uploads/*
```

### Issue: Approval Not Working

**Symptoms:** Upload pending but approve button doesn't work

**Diagnosis:**

```bash
# 1. Verify approval enabled
grep "APPROVAL_REQUIRED" .env
# Should show: APPROVAL_REQUIRED=true

# 2. Check pending images exist
# Admin > Pending Approvals section
# Should show room groups with thumbnails

# 3. Check JavaScript errors
# Browser F12 > Console

# 4. Check server logs
docker compose logs app | grep approve

# 5. Verify database tables exist
sqlite3 data/qr_rooms.db ".schema pending_images"
```

**Solutions:**

```bash
# If tables missing (old database):
# Delete and recreate:
rm data/qr_rooms.db
docker compose restart app
# DB will auto-init

# If approval not enabled:
# Edit .env:
APPROVAL_REQUIRED=true
docker compose restart app

# If approve button not responding:
# Clear browser cache (Ctrl+Shift+Delete)
# Reload page (Ctrl+F5)
```

### Issue: Server Memory Leak / High CPU

**Diagnosis:**

```bash
# Check resource usage
docker compose stats
# OR
top  # Press 'q' to quit

# Check for stuck processes
ps aux | grep python

# Check log file size (disk full?)
du -sh logs/
du -sh uploads/

# Count images and pending items
sqlite3 data/qr_rooms.db "SELECT COUNT(*) FROM room_images"
sqlite3 data/qr_rooms.db "SELECT COUNT(*) FROM pending_images"
```

**Solutions:**

```bash
# If disk full:
# Reduce AUTO_PURGE_HOURS in .env
# Manually delete old images:
find uploads/ -mtime +7 -delete

# If stuck process:
docker compose restart app

# If memory leak in loop:
# Check APScheduler job
# View scheduler logs
docker compose logs app | grep SCHEDULER
```

---

## Support & Maintenance

### Regular Maintenance Schedule

**Daily:**
- Monitor server disk space
- Check authorization logs for failed logins
- Verify approval queue is being processed

**Weekly:**
- Backup database
- Review upload patterns for anomalies
- Test display devices are online

**Monthly:**
- Comprehensive backup test (restore to test environment)
- Security patches (OS, Python packages)
- Changelog review for app updates
- Performance analysis

**Quarterly:**
- Penetration testing
- Compliance audit
- Staff training refresher
- Disaster recovery drill

### Backup Strategy

**Automated Daily Backup:**

```bash
#!/bin/bash
# /backup/backup-qr-module.sh

BACKUP_DIR="/backup/qr-module"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp /data/qr_rooms.db $BACKUP_DIR/qr_rooms_$TIMESTAMP.db

# Backup .env
cp /app/.env $BACKUP_DIR/.env_$TIMESTAMP

# Compress
tar -czf $BACKUP_DIR/qr-module_$TIMESTAMP.tar.gz \
    $BACKUP_DIR/qr_rooms_$TIMESTAMP.db \
    $BACKUP_DIR/.env_$TIMESTAMP

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Report
echo "Backup completed: $BACKUP_DIR/qr-module_$TIMESTAMP.tar.gz" | \
    mail -s "QR Module Backup" admin@hospital.org
```

**Cron schedule:**

```bash
# Run daily at 2 AM
0 2 * * * /backup/backup-qr-module.sh
```

### Disaster Recovery Procedure

**Scenario: Server Failure (Complete Loss)**

```
1. Provision new server (same specs)
2. Install OS and Docker
3. Clone repository: git clone https://github.com/davidgorley/qr-module.git
4. Restore .env: cp /backup/.env_LATEST .env
5. Restore database: cp /backup/qr_rooms_LATEST.db data/qr_rooms.db
6. Start application: docker compose up -d
7. Verify: curl http://localhost:5000/
8. Test with sample upload
9. Restore displays' URLs if necessary
```

**Estimated recovery time:** 30 minutes  
**Data loss:** ~24 hours (since last backup)

### Version Updates

**Checking for Updates:**

```bash
# In repository directory
git fetch origin
git log origin/main --oneline -5

# Compare versions
git describe --tags origin/main
# Current: git describe --tags
```

**Updating to New Version:**

```bash
# 1. Backup current state
cp data/qr_rooms.db data/qr_rooms.db.backup

# 2. Pull latest
git pull origin main

# 3. Review changelog
cat CHANGELOG.md | head -50

# 4. Restart with new code
docker compose down
docker compose up -d --build

# 5. Verify
curl http://localhost:5000/

# 6. Test key features:
#    - Login still works
#    - Room creation works
#    - Upload works
#    - Slideshow works
```

### Getting Help

**Resources:**

1. **Documentation:** 
   - README.md - Quick start
   - CHANGELOG.md - Version history
   - This file - Complete guide

2. **GitHub Issues:**
   - https://github.com/davidgorley/qr-module/issues
   - Report bugs, request features

3. **Internal IT Support:**
   - Hospital Help Desk (for network/firewall issues)
   - Security team (for access/compliance questions)

**Common Questions:**

**Q: Can I upgrade while deployed?**  
A: Yes, with brief downtime:
```bash
git pull origin main
docker compose down
docker compose up -d --build
# Total: ~2 minutes
```

**Q: How do I export all images?**  
A: Copy from uploads directory:
```bash
tar -czf qr-module-images-backup.tar.gz uploads/
# Then download the .tar.gz file
```

**Q: How do I reset admin password?**  
A: Edit .env and restart:
```
ADMIN_PASSWORD=NewPassword123!
docker compose restart app
```

---

## Summary

QR Module v7.1.0 is a **production-ready image management system** for hospital environments. It provides:

✅ **User-Friendly** - Scan QR code, upload image, done  
✅ **Admin-Controlled** - Centralized room and content management  
✅ **Secure** - Authentication, approval workflow, audit logs  
✅ **Reliable** - Persistent storage, auto-cleanup, monitoring  
✅ **Scalable** - Unlimited rooms and images  
✅ **Compliant** - HIPAA-ready with proper configuration  

**Next Steps for Hospital Deployment:**

1. **Review** this guide with IT and compliance teams
2. **Test** in non-production environment first
3. **Configure** security settings (strong credentials, HTTPS, firewall)
4. **Deploy** using Docker (recommended) or Python
5. **Train** staff on admin and user workflows
6. **Monitor** ongoing operations
7. **Iterate** based on feedback

For questions or support, contact the development team or open an issue on GitHub.

---

**Document Version:** 1.0  
**Last Updated:** February 26, 2026  
**Maintained By:** QR Module Team  
**Classification:** Internal Use
