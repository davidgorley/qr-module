# Changelog

All notable changes to CarePics (formerly QR Module) will be documented in this file.

## [9.0.0] - 2026-04-13

### ✨ New Features
- **IP Address Field** - Room creation now includes optional IP address field for device tracking
- **Device Online/Offline Status** - Devices are pinged every `PING_INTERVAL_SECONDS` to determine online/offline status
  - Status badges show **ONLINE** (green) or **OFFLINE** (red) on room cards
  - Status can be filtered via "Online/Offline" dropdown filter
- **Room Card Redesign** - Per mockup specifications:
  - **Unit** (centered, uppercase) at top
  - **Room - Bed** (centered, bold) as main heading
  - **IP Address** (grey, centered) below heading
  - Status badges: ONLINE/OFFLINE + ADMITTED/VACANT (removed Enabled badge)
  - URL and buttons in two-row layout
- **Unit Filter Dropdown** - Dynamic filter to show rooms by unit only
- **Auto-refresh Functionality**
  - Ping checks every `PING_INTERVAL_SECONDS` (default: 30s, configurable)
  - Room data (admit/vacant status) refreshes every `VACANCY_CHECK_INTERVAL_SECONDS` (default: 30s, configurable)
  - Dashboard updates automatically without page refresh
- **Configurable Timeouts** (.env variables):
  - `PING_ENABLED` - Enable/disable ping checks (default: true)
  - `PING_INTERVAL_SECONDS` - Frequency of device pings (default: 30)
  - `PING_TIMEOUT_SECONDS` - Ping timeout per device (default: 5)
  - `VACANCY_CHECK_INTERVAL_SECONDS` - Frequency of room data refresh (default: 30)

### 🔧 Changed
- `app.py`:
  - Added `ipaddress TEXT` column migration to rooms table
  - Updated `create_room()` endpoint to accept and store `ipaddress`
  - Updated `import_rooms()` endpoint to accept and store `ipaddress` from CSV/XLSX
  - New `POST /api/rooms/ping` endpoint: accepts `{ips: {room_id: ip_address}}`, returns ping results
  - Reads config from `.env`: PING_ENABLED, PING_INTERVAL_SECONDS, PING_TIMEOUT_SECONDS, VACANCY_CHECK_INTERVAL_SECONDS
  - Added logging (INFO level) for ping commands and results
- `templates/admin.html`:
  - Added 4th input field to room creation: "IP Address (e.g., 10.0.0.1)"
  - Added "Unit" filter dropdown (dynamic, populated from room data)
  - Added "Online/Offline" status filter dropdown
  - Passes config variables to JavaScript: `pingEnabled`, `pingIntervalSeconds`, `vacancyCheckIntervalSeconds`
- `static/js/admin.js`:
  - `renderRooms()` completely redesigned card HTML per mockup
  - New unit/status filter logic in `renderRooms()`
  - `pingAllRooms()` now returns Promise, waits before rendering
  - `loadRooms()` waits for ping to complete before rendering cards
  - `createRoom()` now includes `ipaddress` field
  - `populateUnitFilter()` dynamically builds unit dropdown from room data
  - `startAutoRefresh()` sets up two intervals:
    - Ping refresh every `pingIntervalSeconds`
    - Room data refresh every `vacancyCheckIntervalSeconds`
  - Added function `pingAllRooms()` as Promise-based reusable function
- `static/css/admin.css`:
  - Widened `.admin-container` from 1200px to **1600px**
  - Added `.card-unit`, `.card-room-bed`, `.card-ip`, `.card-badges` styles for centered card layout
  - Added `.status-badge.online` (green, #dcfce7 bg) and `.status-badge.offline` (red, #fef2f2 bg)
  - Added `.filter-group select` styling for filter dropdowns
  - Updated `.rooms-controls` with `flex-wrap` for responsive filter layout
  - Added spacing between button groups on cards
- `Dockerfile`:
  - Added `apt-get install iputils-ping` to enable ICMP ping in container
- `.env`:
  - Added 4 new configuration variables for ping and vacancy checks (see Features section)
- `docker-compose.yml`: No changes (container now has ping binary installed via Dockerfile)

### 🐛 Fixed
- **Device status not updating** - Fixed race condition where `renderRooms()` was called before `pingAllRooms()` completed
  - Now `loadRooms()` waits for ping results before rendering
- **Docker ping failures** - Container (`python:3.11-slim`) lacked `ping` command
  - Now installs `iputils-ping` package in Dockerfile
- **Linux ping timeout parameter** - Was passing milliseconds to `-W` flag which expects seconds
  - Fixed: Windows `-w` gets milliseconds, Linux `-W` gets seconds
- **Template variables undefined** - Added Jinja2 conditionals with safe defaults

### 📝 Notes
- CSV/XLSX import now supports `ipaddress` column (optional, alongside unit/room/bed)
- Admission/vacancy status now updates every 30s without refresh (via HL7 integration)
- Online/offline status updates every 30s via automated ping checks
- All timestamps configurable — adjust `.env` for your network environment

---

## [8.1.0] - 2026-04-10

### ✨ New Features
- **CarePics Rebranding** - Project renamed from "QR Module" to **CarePics** across all user-facing pages
- **Login Page Redesign** - New CareStream-style login with "CarePics" title, "POWERED BY" Alairo Solutions logo, and blue "Sign In" button
- **Dashboard Navbar** - Added fixed top navigation bar with Alairo logo, "CarePics" branding, "Patient Room Media Manager" subtitle, and nav links
- **Alairo Solutions Logo** - Added Alairo Solutions logo asset at `/static/images/alairo-logo.png`

### 🔧 Changed
- `templates/login.html`:
  - Title: "QR Module - Login" → "CarePics - Login"
  - Heading: "🎯 QR Module" → "CarePics" with "POWERED BY" + Alairo logo
  - Subtitle: "Admin Access" removed, replaced with logo branding
  - Button: "Login" → "➡ Sign In"
- `templates/admin.html`:
  - Title: "QR Module - Admin" → "CarePics - Dashboard"
  - Added `<nav class="top-navbar">` with Alairo logo, CarePics title, and nav links
  - Heading: "🎯 QR Module - Room Management" → "📋 Room Dashboard"
  - Logout button moved from admin header into navbar
- `templates/display.html`: Title "QR Display" → "CarePics Display"
- `static/css/login.css`:
  - Background gradient: purple (#667eea → #764ba2) → blue (#1e3a8a → #2563eb → #1e40af)
  - All accent colors updated from purple to blue (#2563eb)
  - Added styles for `.app-title`, `.powered-by`, `.alairo-logo`
- `static/css/admin.css`:
  - Body background: purple gradient → light steel blue (#b8c5d3)
  - Added full `.top-navbar` styling (fixed position, dark blue gradient)
  - Heading color: white → dark grey (#2d3748)
  - All accent colors: purple (#667eea) → blue (#2563eb)
  - Sort buttons, badges, create button, modal all updated to blue scheme
  - Added responsive rules (navbar subtitle hidden on mobile)
- `static/images/alairo-logo.png`: New Alairo Solutions logo asset

### 📝 Notes
- No backend changes; all routes, API endpoints, and database remain unchanged
- JavaScript logic untouched — all functions (login, logout, CRUD, polling) work as before

---

## [8.0.0] - 2026-04-10

### ✨ New Features
- **HL7 Integration** - Real-time ADT event processing via webhook from hl7-service
  - **Discharge (A03)**: Automatically clears all images when a patient is discharged
  - **Admit (A01)**: Marks room as patient-admitted for tracking
  - **Transfer (A02)**: Clears images at old location and marks new location as admitted
- **HL7 Webhook Endpoint** - `POST /api/hl7/event` receives ADT events with shared-secret authentication
- **HL7 Health Check** - `GET /api/hl7/status` for hl7-service to verify connectivity
- **ADT Debug Endpoint** - `GET /api/adt/debug` runs a manual discharge check cycle with detailed diagnostics
- **ADT Discharge Polling (fallback)** - Scheduled polling against Nexus API as backup when HL7 events are unavailable
- **Nexus API Integration** - JWT-authenticated queries to Nexus patient management system for admitted patient lists
- **Room Location Matching** - Cascading match algorithm (exact unit/room/bed → room+bed → room-only) to map hospital locations to rooms
- **Structured Room Creation** - Rooms now require Unit, Room Number, and Bed fields instead of free-text name; display name auto-generated as "{unit} - Room {room_number}, Bed {bed}"

### 🔧 Changed
- `app.py`:
  - Added `validate_webhook_secret` decorator for HL7 webhook authentication
  - Added `clear_images_for_room()` utility (deletes files + DB records for approved and pending images)
  - Added `find_rooms_by_location()` with cascading match strategy
  - Added `get_nexus_jwt_token()` with global JWT caching (28-day expiry)
  - Added `check_discharges()` polling job (configurable interval via `ADT_POLL_INTERVAL`)
  - Added `handle_discharge()`, `handle_admit()`, `handle_transfer()` event handlers
  - Room creation now requires `unit`, `room`, `bed` fields
- `templates/admin.html`: Room creation inputs changed from single name field to Unit, Room Number, and Bed fields

### 📝 New Environment Variables
```
ADT_POLL_ENABLED=true                   # Enable/disable Nexus polling fallback
ADT_POLL_INTERVAL=30                    # Polling interval in seconds
NEXUS_API_URL=http://192.168.1.197:3001 # Nexus patient management API
NEXUS_ADMIN_USERNAME=vizabli            # Nexus admin username
NEXUS_ADMIN_PASSWORD=<password>         # Nexus admin password
HL7_WEBHOOK_ENABLED=true               # Enable/disable HL7 webhook endpoint
HL7_WEBHOOK_SECRET=<secret>            # Shared secret for webhook authentication
```

### 📝 Database Changes
- `rooms` table: Added `unit TEXT`, `room TEXT`, `bed TEXT` columns
- `rooms` table: Added `patient_admitted INTEGER DEFAULT 0` column
- Auto-migration adds columns if missing on startup

---

## [7.1.0] - 2026-02-26

### ✨ New Features
- **Admin Login System** - Added secure login page with username/password authentication (configurable via `.env`)
- **Room Enable/Disable Toggle** - Toggle rooms on/off without deleting them; disabled rooms show "Currently Disabled" message on display
- **Media Pre-Approval System** - Optional admin approval workflow for uploaded images (configurable `APPROVAL_REQUIRED` in `.env`)
- **Pending Approvals Section** - Admin panel now shows pending uploads grouped by room with thumbnail previews and quick approve/deny buttons
- **Logout Button** - Added logout functionality to admin panel header
- **Enabled/Disabled Sort Option** - New sort button to show enabled rooms first

### 🔧 Changed
- `app.py`: 
  - Added session management with Flask secret key
  - Added `@login_required` decorator to protected admin routes
  - Updated `/api/rooms` endpoints to support `enabled` column
  - Added `pending_images` table for approval workflow
  - New endpoints: `/login`, `/logout`, `/api/rooms/<id>/toggle`, `/api/pending_images/*` (GET/approve/deny)
  - Modified `/api/save_images` to support approval workflow
  - Modified `/api/get_images` to check room enabled status
- `templates/admin.html`: 
  - Added "Enabled First" sort option
  - Added pending approvals section (shown when approval required)
  - Updated header with logout button
- `templates/display.html`: Added disabled room container showing "Currently Disabled" message
- `templates/login.html`: New login page with form validation
- `static/js/admin.js`:
  - Added `loadPendingApprovals()` function with room grouping
  - Added `toggleRoom()`, `logout()`, `approveImage()`, `denyImage()` functions
  - Updated `renderRooms()` to show status badges and disable toggle buttons
  - Added auto-reload of pending approvals when approving/denying
- `static/js/display.js`: Added `showDisabled()` function to handle disabled rooms
- `static/css/admin.css`: 
  - New styles for header with logout button
  - New pending approvals grid layout (grouped by room)
  - Room status badges and faded styling for disabled rooms
- `static/css/display.css`: New disabled container with pulsing message
- `static/css/login.css`: New login page styling with gradient background
- `.env`: Added authentication and approval system configuration variables

### 🐛 Fixed
- **Image Slideshow with Approvals** - Fixed approve logic to add images instead of replacing them, so multiple approved images rotate correctly in slideshow
- **Pending Approvals UI** - Improved UX by grouping by room with compact thumbnail grid instead of large item list

### 📝 New Environment Variables
```
ADMIN_USERNAME=admin                    # Admin login username
ADMIN_PASSWORD=admin123                 # Admin login password
SECRET_KEY=your-secret-key-change-this # Session encryption (auto-generated if not set)
APPROVAL_REQUIRED=false                 # Enable/disable approval workflow
PENDING_IMAGE_EXPIRY_MINUTES=30         # Auto-delete unapproved images after N minutes
```

### 📝 Database Changes
- `rooms` table: Added `enabled` INTEGER column (DEFAULT 1)
- New `pending_images` table for tracking uploads awaiting approval

### 📝 Breaking Changes
- **Database Migration**: Old databases will auto-migrate on first run (disabled column added)
- **Session Requirements**: All admin routes now require login; existing sessions may be invalidated

---

## [7.0.0] - 2026-02-19

### 🔧 Changed
- `static/js/admin.js`: Added confirmation dialog to `clearRoomImages()` function - users must now confirm before clearing all images from a room via the admin panel

### 📝 Technical Details
- Confirmation uses native browser `confirm()` dialog
- User can cancel the operation; images are only cleared if confirmed

---

## [6.4.1] - 2026-02-19

### ✨ New Features
- **Search & Sort on Admin Panel** - Filter rooms by name/ID with live search and sort by creation date or room name
- **Persistent Database** - SQLite database now persists across Docker container rebuilds via mounted `./data` volume
- **Configurable Slide Duration** - Added `SLIDE_DURATION` environment variable (milliseconds) to control image slideshow timing
- **Clear Button on Admin Cards** - Each room card now has a "Clear" button to remove all images without deleting the room
- **Improved Display UX** - Clear button centered and toned down on display page; removed confirm dialogs for tablet compatibility

### 🔧 Changed
- `docker-compose.yml`: Changed DB mount from `./qr_rooms.db` to `./data:/app/data` for proper file creation
- `app.py`: Updated database path to `data/qr_rooms.db` and ensure `data` folder is created at startup
- `.env`: Added `SLIDE_DURATION=5000` (5 seconds default)
- `templates/admin.html`: Added search input with clear button, replaced select with sort buttons, added results count
- `static/js/admin.js`: Implemented debounced search, sort button toggling, text highlighting in search results, added `clearRoomImages()` function
- `static/css/admin.css`: Styled new search/sort toolbar, sort buttons, highlights, and added `.btn-clear` to room cards
- `templates/display.html`: Removed inline `onclick` from Clear button for better tablet compatibility
- `static/js/display.js`: Changed Clear button to event listener binding, removed confirm dialog for smoother tablet UX
- `static/css/display.css`: Centered Clear button, reduced padding/font-size, lowered opacity (0.6), added mobile media query

### 🐛 Fixed
- Clear button on display page now works reliably on tablets (removed confirm dialog, used event listener)
- Search performance improved with debouncing (250ms)
- Database no longer fails to create when Docker container is rebuilt
- Image slideshow now maintains proper sequence instead of resetting to first image every 3 seconds

### 📝 Technical Details
- Database persistence: Host `./data/` folder mounted to container `/app/data/`
- Search: Client-side filtering with term highlighting
- Slide duration: Configurable via `.env`, passed from server to display template as JavaScript variable

---

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
