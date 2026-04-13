# QR Module v7.1.0

Multi-room QR code system for uploading and displaying images on TV/monitor displays.

## Features

✅ **Multi-Room Support** - Create unlimited rooms with unique QR codes
✅ **QR Code Upload** - Scan with phone to upload images
✅ **Admin Upload** - Upload directly from admin panel (no QR needed)
✅ **Auto-Slideshow** - Rotate multiple images every 10 seconds
✅ **Persistent Storage** - Images survive restarts and reloads
✅ **Auto-Purge** - Automatically delete old images (configurable)
✅ **Fullscreen Display** - Optimized for TV/monitor displays
✅ **Responsive QR Code** - Works on all screen sizes (HD, 4K, 8K)
✅ **HL7 ADT Integration** - Auto-clear images on patient transfer/discharge

## Installation

### Prerequisites
- Docker and Docker Compose installed
- Port 5000 available

### Deployment Steps

```bash
# 1. Extract files
unzip qr-image-transfer-v6.2.zip
cd qr-image-transfer-v6.2

# 2. Configure environment
cp .env.example .env
nano .env  # Edit if needed (default values work)

# 3. Stop old version (if running)
cd ../qr-image-transfer-v6.1  # or whatever old version
docker compose down
cd ../qr-image-transfer-v6.2

# 4. Build and start
docker compose up -d --build

# 5. Verify
docker compose logs -f

# 6. Access
# Admin: http://10.192.128.125:5000
# Display: http://10.192.128.125:5000/display/{room_id}
```

## Usage

### Create a Room
1. Open admin panel: `http://10.192.128.125:5000`
2. Enter Unit, Room Number, and Bed fields (must match your hospital system's location data)
3. Click "Create Room"
4. Click "View Display" to open display page

### ADT Discharge Auto-Clear

The system automatically clears images when patients are discharged or transferred. It polls the hospital's patient management API to detect status changes.

**How it works:**
1. When creating a room, enter Unit, Room, and Bed values matching your hospital system
2. qr-module polls the nexus patient API every 30 seconds
3. When a patient is first detected as admitted, the room is marked as occupied
4. When that patient is no longer admitted (discharged/transferred), all images are automatically cleared
5. The display returns to showing the QR code

**Configuration (`.env`):**
```bash
ADT_POLL_ENABLED=true                           # Enable/disable discharge polling
ADT_POLL_INTERVAL=30                            # Polling interval in seconds
NEXUS_API_URL=http://192.168.1.197:3001         # Nexus admin API URL
```

**No additional services or port mappings required.** Everything runs within qr-module.

### Upload Images (QR Code Method)
1. Scan QR code with phone camera
2. Select one or more images
3. Tap "Upload Images"
4. Images appear on display automatically

### Upload Images (Admin Method)
1. Open admin panel
2. Click "Upload Images" button on room card
3. Select images from computer
4. Click "Upload Images"
5. Images appear on display automatically

### Clear Images
1. Click "Clear" button on display page
2. Confirm deletion
3. Display returns to QR code

## Configuration

Edit `.env` file:

```bash
SERVER_IP=10.192.128.125        # Your server IP
SERVER_PORT=5000                # Port to run on
AUTO_PURGE_ENABLED=true         # Enable auto-purge
AUTO_PURGE_HOURS=48             # Delete images older than 48 hours
```

## Technical Specifications

- **Backend:** Flask 2.3.3 (Python 3.11)
- **Database:** SQLite 3
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **QR Library:** QRCode.js 1.0.0
- **Container:** Docker (Python 3.11-slim)
- **Port:** 5000 (HTTP)
- **Max Upload:** 50MB per file
- **Slideshow Interval:** 10 seconds
- **Polling Interval:** 3 seconds
- **Auto-Purge Interval:** 1 hour

## Troubleshooting

### Container won't start
```bash
docker compose logs -f
```

### Port already in use
Edit `docker-compose.yml` and change `"5000:5000"` to `"8080:5000"`

### ADT Discharge Auto-Clear Not Working
- Check logs: `docker compose logs -f qr-module | grep "\[ADT\]"`
- Verify `ADT_POLL_ENABLED=true` in `.env`
- Verify `NEXUS_API_URL` points to the correct nexus admin API (default: `http://192.168.1.197:3001`)
- Verify room Unit, Room, and Bed fields exactly match nexus bed data
- If logs show "Cannot reach nexus API", check network connectivity between containers

### Images not appearing
- Check network connectivity
- Verify server IP in `.env` matches actual IP
- Check browser console for errors

### Database permission errors
Database is stored inside container (no permission issues)

## Version History

See CHANGELOG.md for detailed version history.

## Support

For issues or questions, refer to the complete technical documentation in `V6.2_COMPLETE_DOCUMENTATION.txt`.
