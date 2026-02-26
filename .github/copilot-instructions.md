# Copilot Instructions for QR Module v6.2

## Project Overview
QR Module is a multi-room image management system for TV/monitor displays. Users scan QR codes to upload images that display as automated slideshows.

## Architecture

### Backend (Flask)
- **Core file:** [app.py](../app.py) - Router, DB logic, file handling
- **Database:** SQLite (persisted in `/data/qr_rooms.db`)
- **Scheduling:** APScheduler for auto-purge job (hourly, configurable age threshold)
- **File storage:** Direct filesystem in `/uploads/` (survives restarts via Docker volume)

### Database Schema
```
rooms table: id (PK), name, created_at
room_images table: id (PK), room_id (FK), image_path, uploaded_at
```
Cascade deletes on room removal. Image references stored as file paths, not blobs.

### Frontend (Vanilla JavaScript)
- **Admin panel** ([templates/admin.html](../templates/admin.html), [static/js/admin.js](../static/js/admin.js)): Room CRUD, upload modal, search/sort
- **Display page** ([templates/display.html](../templates/display.html), [static/js/display.js](../static/js/display.js)): QR code generation, image polling, slideshow (10s default)
- **Upload page** ([templates/upload.html](../templates/upload.html), [static/js/upload.js](../static/js/upload.js)): Mobile-friendly image picker
- **Polling mechanism:** Display page checks `/api/get_images/{room_id}` every 3 seconds (hardcoded, not config)

## Key Workflows

### Start Development
```bash
# Using Docker (production-like)
docker compose up -d --build

# Direct Python (debugging)
python app.py  # Sets up DB, starts scheduler, runs on http://0.0.0.0:5000
```

### Database Reset
Delete `data/qr_rooms.db` to recreate schema on next run (`init_db()` creates tables if missing).

## Essential Code Patterns

### File Handling
**Room-scoped storage:** Files named `{room_id}_{uuid_hex}_{original_name}` to prevent collisions and enable safe deletion.
```python
# Example: "a1b2c3d4_9f7e2c1a_photo.jpg"
unique_filename = f"{room_id}_{uuid.uuid4().hex[:8]}_{file.filename}"
filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
```

### API Design
- **Image upload:** POST `/api/save_images/{room_id}` - replaces all images atomically (deletes old files, clears DB, inserts new)
- **Image fetch:** GET `/api/get_images/{room_id}` - returns URLs (not paths) for client redirect
- **Room deletion:** DELETE `/api/rooms/{room_id}` - cascades to files and DB records

### Frontend Data Flow
```
display.js: generateQRCode() → checkForImages() [3s polling]
     ↓
If images exist: showImages() → startSlideshow()
If empty: showQRCode()
```

### HTML Sanitization
Always use `escapeHtml()` utility in admin.js before rendering user input (room names in search results).
```javascript
const html = `<h3>${highlight(room.name, searchTerm)}</h3>`;  // Safe via escapeHtml()
```

## Configuration

All via `.env` file (Docker and direct Python read it):
```
SERVER_IP=10.192.128.125        # Must match client network expectations
SERVER_PORT=5000
AUTO_PURGE_ENABLED=true
AUTO_PURGE_HOURS=48
SLIDE_DURATION=10000            # Slideshow interval in milliseconds
```

## Common Modifications

**Change slideshow speed:** Update `SLIDE_DURATION` in `.env` or pass `slide_duration` to display.html template.

**Disable image auto-purge:** Set `AUTO_PURGE_ENABLED=false` in `.env`; scheduler job still starts but returns early.

**Add new API endpoint:** 
1. Create route in [app.py](../app.py) following `@app.route()` pattern
2. Return `jsonify()` for consistency
3. Add corresponding fetch call in frontend JS

**Database queries:** Use `db.row_factory = sqlite3.Row` (see [app.py](../app.py) `get_db()`) to treat results as dicts, not tuples.

## Testing Checklist
- Room creation/deletion without orphaned files
- Multi-image uploads replace previous images atomically
- QR code links work from mobile phones on network
- Slideshow rotates at configured interval
- Auto-purge job deletes files older than threshold without breaking display

## Performance Notes
- Max file size: 50MB (enforced by Flask `MAX_CONTENT_LENGTH`)
- No caching on image URLs (always fresh from `/uploads/`)
- Display page polling is client-side only (no server push)
- Auto-purge runs hourly regardless of image count (minimal overhead)
