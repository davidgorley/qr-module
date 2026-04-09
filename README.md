# QR Module v7.1.0

Multi-room QR code system for uploading and displaying images on TV/monitor displays.

## Features

✅ **Multi-Room Support** - Create unlimited rooms with unique QR codes
✅ **QR Code Upload** - Scan with phone to upload images
✅ **Admin Upload** - Upload directly from admin panel (no QR needed)
✅ **Auto-Slideshow** - Rotate multiple images every 10 seconds
✅ **Persistent Storage** - Images survive restarts and reloads
✅ **Auto-Purge** - Automatically delete old images (configurable)
✅ **HL7 Integration** - Clear images on patient discharge (A02/A03 messages)
✅ **Fullscreen Display** - Optimized for TV/monitor displays
✅ **Responsive QR Code** - Works on all screen sizes (HD, 4K, 8K)

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
2. Enter room name (e.g., "Room 201")
3. Click "Create Room"
4. Click "View Display" to open display page

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
SLIDE_DURATION=10000            # Slideshow interval in milliseconds
APPROVAL_REQUIRED=false         # Require approval for uploads
HL7_ENABLED=true                # Enable HL7 integration
HL7_PORT=2575                   # HL7 listener port
```

## HL7 Integration

The QR Module can automatically clear images from a room when HL7 ADT messages are received (A02 - Patient Transfer, A03 - Patient Discharge).

### How It Works

1. **Room Location Mapping**: When creating a room in the admin panel, you specify Unit, Room Number, and Bed
2. **HL7 Listener**: The system listens on the HL7 port (default 2575) for incoming ADT messages
3. **Auto-Clear**: When an A02 or A03 message is received for a patient in that location, all images are automatically cleared from the display
4. **ACK Response**: The system sends back an HL7 acknowledgement (MSA) confirming the message was processed

### Configuration

Enable/disable HL7 integration in `.env`:
```bash
HL7_ENABLED=true       # Enable HL7 listener
HL7_PORT=2575          # Port to listen on (change if needed)
```

**Note:** The HL7 port must be accessible from your hospital HIS/ADT system. Ensure firewall rules allow inbound connections to this port.

### Room Setup Example

If your HL7 patient location is structured as:
- Unit: `GT MS`
- Room: `5201`
- Bed: `1`

Then create a room in the admin panel with those exact values. When an A02/A03 is received with that location, images are cleared immediately.

## Technical Specifications

- **Backend:** Flask 2.3.3 (Python 3.11)
- **Database:** SQLite 3
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **QR Library:** QRCode.js 1.0.0
- **Container:** Docker (Python 3.11-slim)
- **HTTP Port:** 5000
- **HL7 Port:** 2575 (default, configurable)
- **Max Upload:** 50MB per file
- **Slideshow Interval:** 10 seconds
- **Polling Interval:** 3 seconds
- **Auto-Purge Interval:** 1 hour
- **HL7 Support:** ADT A02 (Patient Transfer) & A03 (Patient Discharge)

## Troubleshooting

### Container won't start
```bash
docker compose logs -f
```

### Port already in use
Edit `docker-compose.yml` and change `"5000:5000"` to `"8080:5000"`

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
