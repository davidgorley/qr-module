# Changelog

All notable changes to QR Image Transfer will be documented in this file.

## [6.2] - 2024-02-17

### 🐛 Fixed
- QR code display on all screen sizes (HD, 4K, 8K, etc.)
- QR code no longer zoomed in or cropped on high-resolution displays

### 🔧 Changed
- `display.css`: QR container from fixed 80vh to responsive auto with 90vw/vh max
- `display.css`: Added canvas/img responsive styling with object-fit: contain
- `.env.example`: Removed unused auth variables (ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY, INTERNAL_NETWORK)
- QR code now scales automatically based on viewport size

### 📝 Technical Details
- Container: width/height auto with max-width: 90vw, max-height: 90vh
- QR generation: 300x300 pixels (maintained from v6.1)
- Tested on 3840x2160 (4K) display at 480 DPI

---

## [6.1] - 2024-02-16

### ✨ New Features
- **Admin Upload Feature** - Upload images directly from admin panel without QR code
- Upload modal with image preview
- Click "Upload Images" button on any room card
- Direct admin-to-display upload (no phone needed)

### 🐛 Fixed
- Database permission errors - Database now stored inside container (not mounted)
- QR code scaling issues - Changed to 80vh and perfectly centered
- Clear button now works on both display AND admin panel
- Multiple image upload no longer drops files
- Docker volume mount issues - Removed problematic DB mount

### 🔧 Changed
- `docker-compose.yml`: Removed database volume mount
- `app.py`: Database stored in container filesystem
- `admin.html`: Added upload modal
- `admin.css`: Added modal styling
- `admin.js`: Added upload modal logic

---

## [6.0] - 2024-02-15

### ✨ New Features
- Admin panel upload capability
- Upload images without QR code

---

## [2.1.0] - 2024-02-14

### 🐛 Fixed
- QR code appearing zoomed in/cropped on 4K displays (3840x2160)

### 🔧 Changed
- QR generation size from 512x512 to 300x300 pixels
- CSS from fixed 80vmin to responsive auto with 90vw/vh max

---

## [2.0.1] - 2024-02-13

### 🔧 Changed
- Updated server IP from 10.192.128.25 to 10.192.128.125

---

## [2.0.0] - 2024-02-12

### ✨ New Features
- Migrated from WordPress plugin to Flask standalone app
- Docker containerization
- SQLite database for persistence
- Auto-purge functionality

### 🔧 Changed
- Complete rewrite in Python/Flask
- Removed WordPress dependencies

---

## [1.3] - 2024-02-11

### 🐛 Fixed
- Images lost on page reload
- Images now persist in database instead of transients

### ✨ New Features
- `wp_qr_room_images` database table for persistent storage
- Automatic image check on page load

---

## [1.2] - 2024-02-10

### ✨ New Features
- Admin panel to manage multiple QR codes
- Create/edit/delete rooms
- Generate unique shortcodes per room
- Multiple image upload support
- Auto-slideshow (10-second rotation)

### 🔧 Changed
- Added `wp_qr_rooms` custom database table
- Updated AJAX handlers for multiple images
- Enhanced frontend JavaScript for slideshow

---

## [1.1] - 2024-02-09

### 🔧 Changed
- Removed all initial text and elements (QR code only)
- Removed text above uploaded images
- Added "Clear" button under uploaded image
- Made QR code and images fill 100% of window (responsive)
- Optimized for TV display as dashboard module

---

## [1.0] - 2024-02-08

### ✨ Initial Release
- WordPress plugin
- QR code generation
- Mobile image upload
- Display page for TV/monitor
- Basic room management
