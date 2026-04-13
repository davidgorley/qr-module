from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps
import secrets
import logging
import subprocess
import re
import requests as http_requests

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

# Ping and Status Check Configuration
PING_ENABLED = os.getenv('PING_ENABLED', 'true').lower() == 'true'
PING_INTERVAL_SECONDS = int(os.getenv('PING_INTERVAL_SECONDS', '30'))
PING_TIMEOUT_SECONDS = int(os.getenv('PING_TIMEOUT_SECONDS', '5'))
VACANCY_CHECK_INTERVAL_SECONDS = int(os.getenv('VACANCY_CHECK_INTERVAL_SECONDS', '30'))

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
APPROVAL_REQUIRED = os.getenv('APPROVAL_REQUIRED', 'false').lower() == 'true'
PENDING_IMAGE_EXPIRY_MINUTES = int(os.getenv('PENDING_IMAGE_EXPIRY_MINUTES', '30'))

# ADT Discharge Polling (fallback)
ADT_POLL_ENABLED = os.getenv('ADT_POLL_ENABLED', 'true').lower() == 'true'
ADT_POLL_INTERVAL = int(os.getenv('ADT_POLL_INTERVAL', '30'))
NEXUS_API_URL = os.getenv('NEXUS_API_URL', 'http://192.168.1.197:3001')
NEXUS_ADMIN_USERNAME = os.getenv('NEXUS_ADMIN_USERNAME', 'vizabli')
NEXUS_ADMIN_PASSWORD = os.getenv('NEXUS_ADMIN_PASSWORD', '4vizi2use')

# HL7 Webhook (real-time discharge/admit events from hl7-service)
HL7_WEBHOOK_ENABLED = os.getenv('HL7_WEBHOOK_ENABLED', 'true').lower() == 'true'
HL7_WEBHOOK_SECRET = os.getenv('HL7_WEBHOOK_SECRET', '')

# Global JWT token cache for nexus API
nexus_jwt_token = None
nexus_jwt_expiry = None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            unit TEXT,
            room TEXT,
            bed TEXT,
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
    
    # Add unit, room, bed columns if they don't exist (migration)
    try:
        db.execute('ALTER TABLE rooms ADD COLUMN unit TEXT')
    except:
        pass
    
    try:
        db.execute('ALTER TABLE rooms ADD COLUMN room TEXT')
    except:
        pass
    
    try:
        db.execute('ALTER TABLE rooms ADD COLUMN bed TEXT')
    except:
        pass
    
    try:
        db.execute('ALTER TABLE rooms ADD COLUMN patient_admitted INTEGER DEFAULT 0')
    except:
        pass
    
    try:
        db.execute('ALTER TABLE rooms ADD COLUMN ipaddress TEXT')
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
    if ADT_POLL_ENABLED:
        scheduler.add_job(func=check_discharges, trigger="interval", seconds=ADT_POLL_INTERVAL)
        print(f"[ADT] Discharge polling enabled: every {ADT_POLL_INTERVAL}s against {NEXUS_API_URL}")
    scheduler.start()
    print(f"[SCHEDULER] Auto-purge enabled: every 1 hour (deletes images older than {AUTO_PURGE_HOURS}h)")

# ============================================================================
# ADT Discharge Polling - Checks nexus API for patient status changes
# ============================================================================

def clear_images_for_room(room_id):
    """Clear all images (approved + pending) from a room by room_id."""
    try:
        db = get_db()
        images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()
        pending = db.execute('SELECT image_path FROM pending_images WHERE room_id = ?', (room_id,)).fetchall()
        
        for img in images + pending:
            filepath = img['image_path']
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError as e:
                    logger.warning(f'[ADT] Could not delete file {filepath}: {str(e)}')
        
        db.execute('DELETE FROM room_images WHERE room_id = ?', (room_id,))
        db.execute('DELETE FROM pending_images WHERE room_id = ?', (room_id,))
        db.commit()
        db.close()
        return len(images) + len(pending)
    except Exception as e:
        logger.error(f'[ADT] Error clearing images for room {room_id}: {str(e)}')
        return 0

def find_rooms_by_location(unit=None, room=None, bed=None):
    """
    Find QR module rooms matching a hospital location.
    Matches on room number (required), optionally narrowing by unit and bed.
    Returns list of matching room dicts.
    """
    db = get_db()
    
    if unit and room and bed:
        # Exact match on all three fields
        rooms = db.execute(
            'SELECT id, name, unit, room, bed, patient_admitted FROM rooms WHERE room = ? AND unit = ? AND bed = ?',
            (room, unit, bed)
        ).fetchall()
    elif room and bed:
        # Match on room + bed
        rooms = db.execute(
            'SELECT id, name, unit, room, bed, patient_admitted FROM rooms WHERE room = ? AND bed = ?',
            (room, bed)
        ).fetchall()
    elif room:
        # Match on room number alone (broadest match)
        rooms = db.execute(
            'SELECT id, name, unit, room, bed, patient_admitted FROM rooms WHERE room = ?',
            (room,)
        ).fetchall()
    else:
        rooms = []
    
    db.close()
    return [dict(r) for r in rooms]

def get_nexus_jwt_token():
    """
    Authenticate with nexus admin API and return JWT token.
    Caches the token to avoid repeated logins.
    """
    global nexus_jwt_token, nexus_jwt_expiry
    from datetime import datetime, timedelta
    
    # If token exists and not expired, return cached token
    if nexus_jwt_token and nexus_jwt_expiry and datetime.now() < nexus_jwt_expiry:
        return nexus_jwt_token
    
    try:
        logger.info(f'[ADT] Authenticating with Nexus at {NEXUS_API_URL}/api/auth/login')
        response = http_requests.post(
            f'{NEXUS_API_URL}/api/auth/login',
            json={
                'username': NEXUS_ADMIN_USERNAME,
                'password': NEXUS_ADMIN_PASSWORD
            },
            timeout=10
        )
        
        logger.info(f'[ADT] Auth response: HTTP {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            # Try multiple possible token field names
            token = data.get('token') or data.get('accessToken') or data.get('access_token')
            success = data.get('success', True)  # Some APIs don't have a success field
            
            if token:
                nexus_jwt_token = token
                nexus_jwt_expiry = datetime.now() + timedelta(days=28)
                logger.info('[ADT] JWT token obtained successfully')
                return nexus_jwt_token
            else:
                logger.error(f'[ADT] Auth response has no token. Keys in response: {list(data.keys())}')
                logger.error(f'[ADT] Full auth response: {str(data)[:500]}')
                return None
        
        logger.error(f'[ADT] Auth failed: HTTP {response.status_code} - {response.text[:300]}')
        return None
    except http_requests.exceptions.ConnectionError as e:
        logger.error(f'[ADT] Cannot connect to Nexus at {NEXUS_API_URL}: {str(e)}')
        return None
    except Exception as e:
        logger.error(f'[ADT] Auth exception: {type(e).__name__}: {str(e)}')
        return None

def check_discharges():
    """
    Poll the nexus admin API for currently admitted patients.
    Compare against qr-module rooms to detect discharges.
    """
    try:
        # Get JWT token
        token = get_nexus_jwt_token()
        if not token:
            return
        
        # Query nexus for all currently admitted patients
        url = f'{NEXUS_API_URL}/api/patients/paginate'
        payload = {
            'filter': {'status': 'ADMITTED'},
            'pagination': {'page': 1, 'limit': 1000},
            'sort': {'updatedAt': 'DESC'}
        }
        
        response = http_requests.post(
            url,
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json=payload,
            timeout=15
        )
        
        if response.status_code == 401:
            # Token expired or invalid — clear cache and retry next cycle
            global nexus_jwt_token, nexus_jwt_expiry
            nexus_jwt_token = None
            nexus_jwt_expiry = None
            logger.warning('[ADT] Nexus returned 401 - token cleared, will re-auth next cycle')
            return
        
        if response.status_code != 200:
            logger.warning(f'[ADT] Nexus API returned HTTP {response.status_code}: {response.text[:200]}')
            return
        
        data = response.json()
        
        # Handle multiple possible response formats from Nexus API
        # Could be: { list: [...] } or { docs: [...] } or { patients: [...] } or { data: [...] } or just [...]
        if isinstance(data, list):
            patients = data
        else:
            patients = data.get('list') or data.get('docs') or data.get('patients') or data.get('data') or data.get('results') or []
        
        logger.info(f'[ADT] Nexus returned {len(patients)} admitted patients (response keys: {list(data.keys()) if isinstance(data, dict) else "array"})')
        
        # Build set of currently occupied beds
        # Log the first patient's structure so we can see the actual field names
        occupied_beds = set()
        occupied_rooms = set()  # Also track just room numbers for fallback matching
        
        if patients and len(patients) > 0:
            # Log first patient structure to debug field names (only first poll or on error)
            sample = patients[0]
            bed_field = sample.get('bed')
            logger.info(f'[ADT] Sample patient keys: {list(sample.keys())}')
            if bed_field:
                if isinstance(bed_field, dict):
                    logger.info(f'[ADT] Sample bed object keys: {list(bed_field.keys())}')
                    logger.info(f'[ADT] Sample bed values: {dict(bed_field)}')
                elif isinstance(bed_field, str):
                    logger.info(f'[ADT] Bed field is a string: "{bed_field}"')
            
            # Also check for location/room info at the patient level
            for key in ['location', 'room', 'roomNo', 'pointOfCare', 'unit', 'assignedBed', 'bedAssignment']:
                if key in sample:
                    logger.info(f'[ADT] Patient has field "{key}": {sample[key]}')
        
        for patient in patients:
            bed_data = patient.get('bed')
            
            if bed_data and isinstance(bed_data, dict):
                # Try multiple possible field names for the bed object
                unit = str(bed_data.get('unit') or bed_data.get('pointOfCare') or bed_data.get('nursingUnit') or bed_data.get('ward') or '').strip()
                room_no = str(bed_data.get('room') or bed_data.get('roomNo') or bed_data.get('roomNumber') or '').strip()
                bed_no = str(bed_data.get('bedNo') or bed_data.get('bed') or bed_data.get('bedNumber') or bed_data.get('bedId') or '').strip()
                
                if unit and room_no and bed_no:
                    occupied_beds.add(f"{unit}|{room_no}|{bed_no}")
                if room_no:
                    occupied_rooms.add(room_no)
                    
            elif bed_data and isinstance(bed_data, str):
                # Bed might be a simple string like "5201-1" or "GT MS|5201|1"
                occupied_rooms.add(bed_data)
            
            # Also check patient-level room fields
            room_val = patient.get('room') or patient.get('roomNo') or patient.get('roomNumber')
            if room_val:
                occupied_rooms.add(str(room_val).strip())
        
        logger.info(f'[ADT] Occupied beds (exact): {occupied_beds}')
        logger.info(f'[ADT] Occupied rooms (room# only): {occupied_rooms}')
        
        # Get all qr-module rooms that have location fields configured
        db = get_db()
        rooms = db.execute('''
            SELECT id, name, unit, room, bed, patient_admitted FROM rooms
            WHERE room IS NOT NULL AND room != ''
        ''').fetchall()
        
        if not rooms:
            logger.info('[ADT] No QR rooms with location data configured - nothing to check')
            db.close()
            return
        
        logger.info(f'[ADT] Checking {len(rooms)} QR room(s) against admitted patients')
        
        for room in rooms:
            room_unit = (room['unit'] or '').strip()
            room_num = (room['room'] or '').strip()
            room_bed = (room['bed'] or '').strip()
            bed_key = f"{room_unit}|{room_num}|{room_bed}"
            
            # Check occupancy: try exact match first, fall back to room number only
            is_occupied = False
            if room_unit and room_num and room_bed:
                is_occupied = bed_key in occupied_beds
            
            if not is_occupied and room_num:
                # Fallback: check if room number appears in occupied rooms
                is_occupied = room_num in occupied_rooms
            
            if is_occupied:
                # Patient is currently admitted in this bed
                if not room['patient_admitted']:
                    db.execute('UPDATE rooms SET patient_admitted = 1 WHERE id = ?', (room['id'],))
                    logger.info(f'[ADT] Patient detected in "{room["name"]}" ({bed_key})')
            else:
                # No admitted patient in this bed
                if room['patient_admitted']:
                    # Was admitted before, now discharged/transferred — clear images!
                    count = clear_images_for_room(room['id'])
                    db.execute('UPDATE rooms SET patient_admitted = 0 WHERE id = ?', (room['id'],))
                    logger.info(f'[ADT] *** DISCHARGE DETECTED *** Cleared {count} images from "{room["name"]}" ({bed_key})')
                # Not logging "still empty" to avoid spam
        
        db.commit()
        db.close()
        
    except http_requests.exceptions.ConnectionError:
        logger.warning(f'[ADT] Cannot reach Nexus API at {NEXUS_API_URL} - will retry')
    except Exception as e:
        logger.error(f'[ADT] Error in check_discharges: {type(e).__name__}: {str(e)}')
        import traceback
        logger.error(f'[ADT] {traceback.format_exc()}')

# ============================================================================
# HL7 Webhook Endpoint - Real-time ADT event processing
# ============================================================================

def validate_webhook_secret(f):
    """Decorator to validate HL7 webhook bearer token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not HL7_WEBHOOK_ENABLED:
            return jsonify({'success': False, 'error': 'HL7 webhook is disabled'}), 503
        
        if HL7_WEBHOOK_SECRET:
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                logger.warning('[HL7-WEBHOOK] Request missing Authorization header')
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
            
            token = auth_header[7:]  # Strip 'Bearer '
            if not secrets.compare_digest(token, HL7_WEBHOOK_SECRET):
                logger.warning('[HL7-WEBHOOK] Invalid webhook secret')
                return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/hl7/event', methods=['POST'])
@validate_webhook_secret
def hl7_event():
    """
    Webhook endpoint for HL7 ADT events from hl7-service.
    
    Expected JSON payload:
    {
        "event_type": "A03",         # A01=admit, A02=transfer, A03=discharge
        "unit": "GT MS",             # PV1-3.1 - Point of Care / Nursing Unit
        "room": "5201",              # PV1-3.2 - Room number (matches deviceId)
        "bed": "1",                  # PV1-3.3 - Bed
        "patient_id": "12345",       # PID-3 (optional, for logging)
        "patient_name": "DOE^JOHN",  # PID-5 (optional, for logging)
        "previous_unit": "",         # For A02 transfers: old unit
        "previous_room": "",         # For A02 transfers: old room
        "previous_bed": ""           # For A02 transfers: old bed
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON payload'}), 400
    
    event_type = data.get('event_type', '').upper().strip()
    unit = data.get('unit', '').strip()
    room = data.get('room', '').strip()
    bed = data.get('bed', '').strip()
    patient_id = data.get('patient_id', 'unknown')
    patient_name = data.get('patient_name', 'unknown')
    
    if not room:
        return jsonify({'success': False, 'error': 'Room number is required'}), 400
    
    location_str = f"{unit} Room {room} Bed {bed}" if unit and bed else f"Room {room}"
    logger.info(f'[HL7-WEBHOOK] Received {event_type} for patient {patient_id} at {location_str}')
    
    if event_type == 'A03':
        # DISCHARGE - Clear all media for this room
        return handle_discharge(unit, room, bed, patient_id, location_str)
    
    elif event_type == 'A01':
        # ADMIT - Mark room as having a patient
        return handle_admit(unit, room, bed, patient_id, location_str)
    
    elif event_type == 'A02':
        # TRANSFER - Clear old location, mark new as admitted
        prev_unit = data.get('previous_unit', '').strip()
        prev_room = data.get('previous_room', '').strip()
        prev_bed = data.get('previous_bed', '').strip()
        return handle_transfer(unit, room, bed, prev_unit, prev_room, prev_bed, patient_id, location_str)
    
    else:
        logger.info(f'[HL7-WEBHOOK] Ignoring event type {event_type}')
        return jsonify({'success': True, 'action': 'ignored', 'message': f'Event type {event_type} not handled'})

def handle_discharge(unit, room, bed, patient_id, location_str):
    """Process A03 discharge: clear all images from matching room(s)."""
    matching_rooms = find_rooms_by_location(unit, room, bed)
    
    if not matching_rooms:
        logger.info(f'[HL7-WEBHOOK] No QR rooms match {location_str} - no action needed')
        return jsonify({'success': True, 'action': 'no_match', 'message': f'No QR rooms found for {location_str}'})
    
    total_cleared = 0
    cleared_rooms = []
    
    db = get_db()
    for qr_room in matching_rooms:
        count = clear_images_for_room(qr_room['id'])
        db.execute('UPDATE rooms SET patient_admitted = 0 WHERE id = ?', (qr_room['id'],))
        total_cleared += count
        cleared_rooms.append(qr_room['name'])
        logger.info(f'[HL7-WEBHOOK] DISCHARGE: Cleared {count} images from "{qr_room["name"]}" (room_id={qr_room["id"]})')
    
    db.commit()
    db.close()
    
    logger.info(f'[HL7-WEBHOOK] Discharge complete for patient {patient_id}: cleared {total_cleared} images from {len(cleared_rooms)} room(s)')
    return jsonify({
        'success': True,
        'action': 'discharged',
        'rooms_cleared': len(cleared_rooms),
        'images_cleared': total_cleared,
        'room_names': cleared_rooms
    })

def handle_admit(unit, room, bed, patient_id, location_str):
    """Process A01 admit: mark matching room(s) as having an admitted patient."""
    matching_rooms = find_rooms_by_location(unit, room, bed)
    
    if not matching_rooms:
        logger.info(f'[HL7-WEBHOOK] No QR rooms match {location_str} for admit')
        return jsonify({'success': True, 'action': 'no_match', 'message': f'No QR rooms found for {location_str}'})
    
    db = get_db()
    for qr_room in matching_rooms:
        db.execute('UPDATE rooms SET patient_admitted = 1 WHERE id = ?', (qr_room['id'],))
        logger.info(f'[HL7-WEBHOOK] ADMIT: Patient admitted at "{qr_room["name"]}" (room_id={qr_room["id"]})')
    
    db.commit()
    db.close()
    
    return jsonify({
        'success': True,
        'action': 'admitted',
        'rooms_updated': len(matching_rooms)
    })

def handle_transfer(unit, room, bed, prev_unit, prev_room, prev_bed, patient_id, location_str):
    """Process A02 transfer: clear old location images, mark new location as admitted."""
    results = {'old_cleared': 0, 'new_admitted': 0}
    
    # Clear images from previous location
    if prev_room:
        prev_location_str = f"{prev_unit} Room {prev_room} Bed {prev_bed}" if prev_unit and prev_bed else f"Room {prev_room}"
        prev_rooms = find_rooms_by_location(prev_unit, prev_room, prev_bed)
        
        db = get_db()
        for qr_room in prev_rooms:
            count = clear_images_for_room(qr_room['id'])
            db.execute('UPDATE rooms SET patient_admitted = 0 WHERE id = ?', (qr_room['id'],))
            results['old_cleared'] += count
            logger.info(f'[HL7-WEBHOOK] TRANSFER: Cleared {count} images from old location "{qr_room["name"]}"')
        db.commit()
        db.close()
    
    # Mark new location as admitted
    new_rooms = find_rooms_by_location(unit, room, bed)
    if new_rooms:
        db = get_db()
        for qr_room in new_rooms:
            db.execute('UPDATE rooms SET patient_admitted = 1 WHERE id = ?', (qr_room['id'],))
            results['new_admitted'] += 1
            logger.info(f'[HL7-WEBHOOK] TRANSFER: Patient now at "{qr_room["name"]}"')
        db.commit()
        db.close()
    
    logger.info(f'[HL7-WEBHOOK] Transfer complete for patient {patient_id}: cleared {results["old_cleared"]} images, admitted to {results["new_admitted"]} room(s)')
    return jsonify({
        'success': True,
        'action': 'transferred',
        'old_images_cleared': results['old_cleared'],
        'new_rooms_admitted': results['new_admitted']
    })

# ============================================================================
# Health/Status endpoint for HL7 service connectivity check
# ============================================================================

@app.route('/api/hl7/status', methods=['GET'])
def hl7_status():
    """Health check endpoint for HL7 service to verify QR module is reachable."""
    return jsonify({
        'status': 'ok',
        'webhook_enabled': HL7_WEBHOOK_ENABLED,
        'poll_enabled': ADT_POLL_ENABLED,
        'version': '6.2'
    })

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/adt/debug', methods=['GET'])
@login_required
def adt_debug():
    """
    Debug endpoint - manually runs one discharge check cycle and returns
    everything it sees so you can diagnose what's working/broken.
    Hit this from your browser while logged into admin:
      http://<SERVER_IP>:5000/api/adt/debug
    """
    result = {
        'config': {
            'NEXUS_API_URL': NEXUS_API_URL,
            'ADT_POLL_ENABLED': ADT_POLL_ENABLED,
            'ADT_POLL_INTERVAL': ADT_POLL_INTERVAL,
            'NEXUS_ADMIN_USERNAME': NEXUS_ADMIN_USERNAME,
        },
        'steps': []
    }
    
    # Step 1: Auth
    try:
        auth_response = http_requests.post(
            f'{NEXUS_API_URL}/api/auth/login',
            json={'username': NEXUS_ADMIN_USERNAME, 'password': NEXUS_ADMIN_PASSWORD},
            timeout=10
        )
        auth_data = auth_response.json() if auth_response.status_code == 200 else auth_response.text[:500]
        token = None
        if isinstance(auth_data, dict):
            token = auth_data.get('token') or auth_data.get('accessToken') or auth_data.get('access_token')
        
        result['steps'].append({
            'step': '1_auth',
            'status': auth_response.status_code,
            'token_found': bool(token),
            'response_keys': list(auth_data.keys()) if isinstance(auth_data, dict) else 'not_json',
            'response_preview': str(auth_data)[:300]
        })
        
        if not token:
            result['error'] = 'Could not obtain JWT token from Nexus'
            return jsonify(result)
    except http_requests.exceptions.ConnectionError as e:
        result['steps'].append({
            'step': '1_auth',
            'error': f'Cannot connect to {NEXUS_API_URL}: {str(e)}'
        })
        result['error'] = f'Cannot reach Nexus at {NEXUS_API_URL}'
        return jsonify(result)
    except Exception as e:
        result['steps'].append({'step': '1_auth', 'error': f'{type(e).__name__}: {str(e)}'})
        return jsonify(result)
    
    # Step 2: Query patients
    try:
        patients_response = http_requests.post(
            f'{NEXUS_API_URL}/api/patients/paginate',
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={
                'filter': {'status': 'ADMITTED'},
                'pagination': {'page': 1, 'limit': 1000},
                'sort': {'updatedAt': 'DESC'}
            },
            timeout=15
        )
        
        result['steps'].append({
            'step': '2_patients_query',
            'status': patients_response.status_code,
            'response_preview': patients_response.text[:500]
        })
        
        if patients_response.status_code != 200:
            result['error'] = f'Patients API returned HTTP {patients_response.status_code}'
            return jsonify(result)
        
        pdata = patients_response.json()
        
        if isinstance(pdata, list):
            patients = pdata
            result['steps'].append({'step': '2b_format', 'type': 'array', 'count': len(patients)})
        else:
            result['steps'].append({'step': '2b_format', 'type': 'object', 'keys': list(pdata.keys())})
            patients = pdata.get('list') or pdata.get('docs') or pdata.get('patients') or pdata.get('data') or pdata.get('results') or []
            result['steps'].append({'step': '2c_patients_found', 'count': len(patients), 'used_key': next((k for k in ['list', 'docs', 'patients', 'data', 'results'] if pdata.get(k)), 'none')})
        
    except Exception as e:
        result['steps'].append({'step': '2_patients_query', 'error': f'{type(e).__name__}: {str(e)}'})
        return jsonify(result)
    
    # Step 3: Inspect patient structure
    if patients:
        sample = patients[0]
        # Sanitize - don't expose actual patient names in debug, but show structure
        sample_keys = list(sample.keys())
        bed_field = sample.get('bed')
        bed_info = None
        if bed_field:
            if isinstance(bed_field, dict):
                bed_info = {'type': 'object', 'keys': list(bed_field.keys()), 'values': {k: str(v) for k, v in bed_field.items()}}
            else:
                bed_info = {'type': type(bed_field).__name__, 'value': str(bed_field)[:100]}
        
        result['steps'].append({
            'step': '3_patient_structure',
            'patient_keys': sample_keys,
            'bed_field': bed_info,
            'has_room_field': 'room' in sample or 'roomNo' in sample,
            'sample_room_fields': {k: str(sample.get(k, ''))[:50] for k in ['room', 'roomNo', 'roomNumber', 'location', 'unit', 'pointOfCare'] if k in sample}
        })
    else:
        result['steps'].append({'step': '3_patient_structure', 'note': 'No admitted patients returned'})
    
    # Step 4: Build occupied beds
    occupied_beds = set()
    occupied_rooms = set()
    
    for patient in patients:
        bed_data = patient.get('bed')
        if bed_data and isinstance(bed_data, dict):
            unit = str(bed_data.get('unit') or bed_data.get('pointOfCare') or bed_data.get('nursingUnit') or bed_data.get('ward') or '').strip()
            room_no = str(bed_data.get('room') or bed_data.get('roomNo') or bed_data.get('roomNumber') or '').strip()
            bed_no = str(bed_data.get('bedNo') or bed_data.get('bed') or bed_data.get('bedNumber') or bed_data.get('bedId') or '').strip()
            if unit and room_no and bed_no:
                occupied_beds.add(f"{unit}|{room_no}|{bed_no}")
            if room_no:
                occupied_rooms.add(room_no)
        elif bed_data and isinstance(bed_data, str):
            occupied_rooms.add(bed_data)
        
        room_val = patient.get('room') or patient.get('roomNo') or patient.get('roomNumber')
        if room_val:
            occupied_rooms.add(str(room_val).strip())
    
    result['steps'].append({
        'step': '4_occupied',
        'exact_beds': sorted(list(occupied_beds)),
        'room_numbers': sorted(list(occupied_rooms)),
    })
    
    # Step 5: Compare with QR rooms
    db = get_db()
    qr_rooms = db.execute('''
        SELECT id, name, unit, room, bed, patient_admitted FROM rooms
        WHERE room IS NOT NULL AND room != ''
    ''').fetchall()
    db.close()
    
    room_status = []
    for room in qr_rooms:
        room_unit = (room['unit'] or '').strip()
        room_num = (room['room'] or '').strip()
        room_bed = (room['bed'] or '').strip()
        bed_key = f"{room_unit}|{room_num}|{room_bed}"
        
        is_occupied = False
        match_type = 'none'
        
        if room_unit and room_num and room_bed and bed_key in occupied_beds:
            is_occupied = True
            match_type = 'exact_bed'
        elif room_num and room_num in occupied_rooms:
            is_occupied = True
            match_type = 'room_number'
        
        would_act = ''
        if is_occupied and not room['patient_admitted']:
            would_act = 'WILL_MARK_ADMITTED'
        elif not is_occupied and room['patient_admitted']:
            would_act = 'WILL_CLEAR_IMAGES (discharge detected!)'
        
        room_status.append({
            'name': room['name'],
            'qr_room_id': room['id'],
            'bed_key': bed_key,
            'currently_occupied_in_nexus': is_occupied,
            'match_type': match_type,
            'patient_admitted_flag': bool(room['patient_admitted']),
            'action': would_act or 'no_change'
        })
    
    result['steps'].append({
        'step': '5_qr_room_comparison',
        'qr_rooms_with_location': len(qr_rooms),
        'rooms': room_status
    })
    
    return jsonify(result)

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
    return render_template('admin.html', server_url=SERVER_URL, approval_required=APPROVAL_REQUIRED, 
                          ping_enabled=PING_ENABLED, ping_interval=PING_INTERVAL_SECONDS, 
                          vacancy_check_interval=VACANCY_CHECK_INTERVAL_SECONDS)

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
    unit = data.get('unit', '').strip()
    room_number = data.get('room', '').strip()
    bed = data.get('bed', '').strip()
    ipaddress = data.get('ipaddress', '').strip()

    # Validate that all three fields are provided
    if not unit or not room_number or not bed:
        return jsonify({'success': False, 'error': 'Unit, Room, and Bed are required'}), 400

    # Auto-generate display name from the three fields
    room_name = f"{unit} - Room {room_number}, Bed {bed}"
    room_id = str(uuid.uuid4())[:8]

    db = get_db()
    db.execute('INSERT INTO rooms (id, name, unit, room, bed, enabled, ipaddress) VALUES (?, ?, ?, ?, ?, ?, ?)', 
               (room_id, room_name, unit, room_number, bed, 1, ipaddress))
    db.commit()
    db.close()

    return jsonify({'success': True, 'room_id': room_id, 'name': room_name, 'unit': unit, 'room': room_number, 'bed': bed, 'ipaddress': ipaddress})

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

@app.route('/api/rooms/ping', methods=['POST'])
@login_required
def ping_rooms():
    if not PING_ENABLED:
        return jsonify({'success': True, 'results': {}})
    
    data = request.json
    ips = data.get('ips', {})  # { room_id: ip_address, ... }
    results = {}
    
    for room_id, ip in ips.items():
        if not ip:
            results[room_id] = False
            continue
        # Validate IP format to prevent command injection
        if not re.match(r'^[\d\.]+$', ip):
            results[room_id] = False
            continue
        
        try:
            # Use ICMP ping to check if device is online
            param = '-n' if os.name == 'nt' else '-c'
            cmd = ['ping', param, '1', ip]
            if os.name == 'nt':
                # Windows -w takes milliseconds
                cmd.extend(['-w', str(PING_TIMEOUT_SECONDS * 1000)])
            else:
                # Linux -W takes seconds
                cmd.extend(['-W', str(PING_TIMEOUT_SECONDS)])
            
            logging.debug(f"Pinging {ip} with command: {' '.join(cmd)}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=PING_TIMEOUT_SECONDS + 2)
            is_online = (result.returncode == 0)
            logging.debug(f"Ping result for {ip}: returncode={result.returncode}, online={is_online}")
            results[room_id] = is_online
        except Exception as e:
            logging.error(f"Error pinging {ip}: {str(e)}")
            results[room_id] = False
    
    return jsonify({'success': True, 'results': results})

@app.route('/api/rooms/import', methods=['POST'])
@login_required
def import_rooms():
    data = request.json
    rooms_data = data.get('rooms', [])
    
    if not rooms_data:
        return jsonify({'success': False, 'error': 'No rooms provided'}), 400
    
    db = get_db()
    imported = 0
    skipped = 0
    
    for room_entry in rooms_data:
        unit = str(room_entry.get('unit', '')).strip()
        room_number = str(room_entry.get('room', '')).strip()
        bed = str(room_entry.get('bed', '')).strip()
        ipaddress = str(room_entry.get('ipaddress', '')).strip()
        
        if not unit or not room_number or not bed:
            skipped += 1
            continue
        
        # Check for duplicate (same unit + room + bed)
        existing = db.execute(
            'SELECT id FROM rooms WHERE unit = ? AND room = ? AND bed = ?',
            (unit, room_number, bed)
        ).fetchone()
        
        if existing:
            skipped += 1
            continue
        
        room_name = f"{unit} - Room {room_number}, Bed {bed}"
        room_id = str(uuid.uuid4())[:8]
        
        db.execute(
            'INSERT INTO rooms (id, name, unit, room, bed, enabled, ipaddress) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (room_id, room_name, unit, room_number, bed, 1, ipaddress)
        )
        imported += 1
    
    db.commit()
    db.close()
    
    return jsonify({'success': True, 'imported': imported, 'skipped': skipped})

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
def clear_images(room_id):
    try:
        logger.info(f'[CLEAR] User clearing images from room {room_id}')
        db = get_db()

        images = db.execute('SELECT image_path FROM room_images WHERE room_id = ?', (room_id,)).fetchall()

        for img in images:
            filepath = img['image_path']
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f'[CLEAR] Deleted file: {filepath}')

        db.execute('DELETE FROM room_images WHERE room_id = ?', (room_id,))
        db.commit()
        db.close()

        logger.info(f'[CLEAR] Successfully cleared {len(images)} images from room {room_id}')
        return jsonify({'success': True, 'cleared': len(images)})
    except Exception as e:
        logger.error(f'[CLEAR] Error clearing images for room {room_id}: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    start_scheduler()
    app.run(host='0.0.0.0', port=5000, debug=False)
