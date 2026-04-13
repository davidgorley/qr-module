let currentRoomId = null;
const modal = document.getElementById('uploadModal');
let allRooms = [];
let currentSort = 'created_desc';
let pingResults = {};
let pingIntervalId = null;
let vacancyCheckIntervalId = null;

function loadRooms() {
    fetch(`${serverUrl}/api/rooms`)
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            return response.json();
        })
        .then(rooms => {
            if (rooms) {
                allRooms = rooms || [];
                populateUnitFilter();
                // PING FIRST before rendering to show correct online/offline status
                pingAllRooms().then(() => {
                    renderRooms();
                    if (approvalRequired) {
                        loadPendingApprovals();
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error loading rooms:', error);
            showAlert('Failed to load rooms');
        });
}

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

function renderRooms() {
    const roomsList = document.getElementById('roomsList');
    if (!allRooms || allRooms.length === 0) {
        roomsList.innerHTML = '<div class="empty-state">No rooms yet. Create your first room above!</div>';
        document.getElementById('resultsCount').textContent = '';
        return;
    }

    const searchVal = (document.getElementById('searchInput')?.value || '').trim();
    const search = searchVal.toLowerCase();
    const unitFilter = (document.getElementById('unitFilter')?.value || '');
    const statusFilter = (document.getElementById('statusFilter')?.value || '');

    let filtered = allRooms.filter(r => {
        if (search && !r.name.toLowerCase().includes(search) && !r.id.toLowerCase().includes(search)) return false;
        if (unitFilter && (r.unit || '') !== unitFilter) return false;
        if (statusFilter === 'online' && !pingResults[r.id]) return false;
        if (statusFilter === 'offline' && pingResults[r.id]) return false;
        return true;
    });

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

    document.getElementById('resultsCount').textContent = `${filtered.length} result${filtered.length !== 1 ? 's' : ''}`;

    const term = searchVal;
    roomsList.innerHTML = filtered.map(room => {
        const isOnline = pingResults[room.id] === true;
        const ipDisplay = room.ipaddress ? escapeHtml(room.ipaddress) : 'No IP';
        return `
        <div class="room-card ${room.enabled === 0 ? 'disabled' : ''}">
            <div class="card-unit">${highlight(room.unit || '', term)}</div>
            <div class="card-room-bed">Room ${highlight(room.room || '', term)} - Bed ${highlight(room.bed || '', term)}</div>
            <div class="card-ip">${ipDisplay}</div>
            <div class="card-badges">
                <span class="status-badge ${isOnline ? 'online' : 'offline'}">
                    ${isOnline ? 'ONLINE' : 'OFFLINE'}
                </span>
                <span class="status-badge ${room.patient_admitted === 1 ? 'admitted' : 'vacant'}">
                    ${room.patient_admitted === 1 ? 'ADMITTED' : 'VACANT'}
                </span>
            </div>
            <div class="room-url" onclick="copyToClipboard('${serverUrl}/display/${room.id}')">
                ${escapeHtml(`${serverUrl}/display/${room.id}`)}
            </div>
            <div class="button-group">
                <button class="btn-view" onclick="viewRoom('${room.id}')">View Display</button>
                <button class="btn-upload" onclick="openUploadModal('${room.id}', '${escapeHtml(room.name)}')">Upload Images</button>
            </div>
            <div class="button-group">
                <button class="btn-toggle ${room.enabled === 1 ? 'btn-disable' : 'btn-enable'}" onclick="toggleRoom('${room.id}')">
                    ${room.enabled === 1 ? 'Disable' : 'Enable'}
                </button>
                <button class="btn-clear" onclick="clearRoomImages('${room.id}')">Clear</button>
                <button class="btn-delete" onclick="deleteRoom('${room.id}')">Delete</button>
            </div>
        </div>
    `}).join('');
}

function createRoom() {
    const unit = document.getElementById('roomUnit').value.trim();
    const room = document.getElementById('roomNumber').value.trim();
    const bed = document.getElementById('roomBed').value.trim();
    const ipaddress = document.getElementById('roomIP').value.trim();

    if (!unit || !room || !bed) {
        alert('Please enter Unit, Room Number, and Bed');
        return;
    }

    fetch(`${serverUrl}/api/rooms`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ unit: unit, room: room, bed: bed, ipaddress: ipaddress })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('roomUnit').value = '';
            document.getElementById('roomNumber').value = '';
            document.getElementById('roomBed').value = '';
            document.getElementById('roomIP').value = '';
            loadRooms();
        } else {
            alert('Failed to create room: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error creating room:', error);
        alert('Failed to create room');
    });
}

function deleteRoom(roomId) {
    if (!confirm('Are you sure you want to delete this room? All images will be removed.')) {
        return;
    }

    fetch(`${serverUrl}/api/rooms/${roomId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadRooms();
        } else {
            alert('Failed to delete room');
        }
    })
    .catch(error => {
        console.error('Error deleting room:', error);
        alert('Failed to delete room');
    });
}

function clearRoomImages(roomId) {
    if (!confirm('Clear all images from this room?')) {
        return;
    }

    fetch(`${serverUrl}/api/clear_images/${roomId}`, {
        method: 'POST'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert(`Successfully cleared ${data.cleared || 0} images`);
            loadRooms();
        } else {
            alert(`Failed to clear images: ${data.error || 'unknown error'}`);
        }
    })
    .catch(error => {
        console.error('Error clearing images:', error);
        alert(`Error: ${error.message}\nMake sure you're logged in to the admin panel`);
    });
}

function viewRoom(roomId) {
    window.open(`${serverUrl}/display/${roomId}`, '_blank');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('URL copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

function openUploadModal(roomId, roomName) {
    currentRoomId = roomId;
    document.getElementById('modalTitle').textContent = `Upload Images to ${roomName}`;
    document.getElementById('modalFileInput').value = '';
    document.getElementById('modalPreview').innerHTML = '';
    document.getElementById('modalStatus').innerHTML = '';
    modal.style.display = 'block';
}

function closeUploadModal() {
    modal.style.display = 'none';
    currentRoomId = null;
}

function handleModalFileSelect(event) {
    const files = event.target.files;
    const preview = document.getElementById('modalPreview');
    preview.innerHTML = '';

    Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            preview.appendChild(img);
        };
        reader.readAsDataURL(file);
    });
}

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
    statusDiv.className = 'modal-status';

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
    })
    .catch(error => {
        console.error('Error uploading images:', error);
        statusDiv.textContent = 'Upload failed: ' + error.message;
        statusDiv.className = 'modal-status error';
    });
}

// Enter key on room input fields triggers createRoom
['roomUnit', 'roomNumber', 'roomBed', 'roomIP'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) {
        el.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') { createRoom(); }
        });
    }
});

document.querySelector('.close').addEventListener('click', closeUploadModal);

window.addEventListener('click', function(e) {
    if (e.target == modal) {
        closeUploadModal();
    }
});

document.getElementById('modalFileInput').addEventListener('change', handleModalFileSelect);

// Hook up improved search/sort controls (debounced search, clear, sort buttons)
const searchInput = document.getElementById('searchInput');
const clearSearchBtn = document.getElementById('clearSearchBtn');
const sortButtons = Array.from(document.querySelectorAll('.sort-btn'));

function debounce(fn, wait) {
    let t;
    return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), wait);
    };
}

const debouncedRender = debounce(() => renderRooms(), 250);

if (searchInput) {
    searchInput.addEventListener('input', debouncedRender);
}

if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
        if (searchInput) {
            searchInput.value = '';
            renderRooms();
            searchInput.focus();
        }
    });
}

sortButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
        sortButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentSort = btn.getAttribute('data-sort') || 'created_desc';
        renderRooms();
    });
});

// Filter event listeners
const unitFilter = document.getElementById('unitFilter');
const statusFilter = document.getElementById('statusFilter');

if (unitFilter) {
    unitFilter.addEventListener('change', () => renderRooms());
}
if (statusFilter) {
    statusFilter.addEventListener('change', () => renderRooms());
}

function populateUnitFilter() {
    const select = document.getElementById('unitFilter');
    if (!select) return;
    const currentVal = select.value;
    const units = [...new Set(allRooms.map(r => r.unit || '').filter(u => u))].sort();
    select.innerHTML = '<option value="">All Units</option>' + units.map(u => `<option value="${escapeHtml(u)}">${escapeHtml(u)}</option>`).join('');
    if (currentVal && units.includes(currentVal)) {
        select.value = currentVal;
    }
}

function pingAllRooms() {
    // Return a Promise so we can wait for ping to complete
    return new Promise((resolve) => {
        console.log('pingEnabled:', typeof pingEnabled !== 'undefined' ? pingEnabled : 'undefined');
        if (typeof pingEnabled !== 'undefined' && !pingEnabled) {
            console.log('Ping disabled, skipping');
            return resolve();
        }
        
        const ips = {};
        allRooms.forEach(r => {
            if (r.ipaddress) {
                ips[r.id] = r.ipaddress;
            }
        });
        
        if (Object.keys(ips).length === 0) {
            console.log('No IPs to ping');
            return resolve();
        }

        console.log('Pinging', Object.keys(ips).length, 'rooms:', ips);
        fetch(`${serverUrl}/api/rooms/ping`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ips: ips })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Ping response:', data);
            if (data.success) {
                pingResults = data.results || {};
                console.log('Ping results stored:', pingResults);
            } else {
                console.error('Ping endpoint returned success=false:', data);
            }
            resolve();
        })
        .catch(error => {
            console.error('Error pinging rooms:', error);
            resolve();
        });
    });
}

function startAutoRefresh() {
    // Set up periodic ping checks
    const pingInterval = typeof pingIntervalSeconds !== 'undefined' ? pingIntervalSeconds : 30;
    if (pingInterval > 0) {
        if (pingIntervalId) clearInterval(pingIntervalId);
        pingIntervalId = setInterval(() => {
            pingAllRooms();
        }, pingInterval * 1000);
        console.log(`Ping auto-refresh started: every ${pingInterval}s`);
    }

    // Set up periodic room data refresh (picks up admit/vacant changes from HL7)
    const vacancyInterval = typeof vacancyCheckIntervalSeconds !== 'undefined' ? vacancyCheckIntervalSeconds : 30;
    if (vacancyInterval > 0) {
        if (vacancyCheckIntervalId) clearInterval(vacancyCheckIntervalId);
        vacancyCheckIntervalId = setInterval(() => {
            fetch(`${serverUrl}/api/rooms`)
                .then(response => {
                    if (response.status === 401) return;
                    return response.json();
                })
                .then(rooms => {
                    if (rooms) {
                        allRooms = rooms || [];
                        populateUnitFilter();
                        renderRooms();
                    }
                })
                .catch(error => console.error('Error refreshing room data:', error));
        }, vacancyInterval * 1000);
        console.log(`Vacancy check auto-refresh started: every ${vacancyInterval}s`);
    }
}

loadRooms();
startAutoRefresh();

function showAlert(msg) {
    alert(msg);
}

function logout() {
    fetch(`${serverUrl}/logout`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/login';
        }
    })
    .catch(error => {
        console.error('Error logging out:', error);
        alert('Error logging out');
    });
}

function toggleRoom(roomId) {
    fetch(`${serverUrl}/api/rooms/${roomId}/toggle`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadRooms();
        } else {
            alert('Failed to toggle room');
        }
    })
    .catch(error => {
        console.error('Error toggling room:', error);
        alert('Failed to toggle room');
    });
}

function loadPendingApprovals() {
    const pendingSection = document.getElementById('pendingSection');
    const pendingList = document.getElementById('pendingList');
    
    let hasPending = false;

    // Load pending images for each room
    const pendingPromises = allRooms.map(room =>
        fetch(`${serverUrl}/api/pending_images/${room.id}`)
            .then(response => response.json())
            .then(data => {
                return { room, pending: data.pending || [] };
            })
            .catch(error => {
                console.error(`Error loading pending images for room ${room.id}:`, error);
                return { room, pending: [] };
            })
    );

    Promise.all(pendingPromises)
        .then(results => {
            const roomsWithPending = results.filter(r => r.pending.length > 0);
            hasPending = roomsWithPending.length > 0;

            if (hasPending) {
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

function approveImage(imageId) {
    fetch(`${serverUrl}/api/pending_images/${imageId}/approve`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadRooms();
        } else {
            alert('Failed to approve image');
        }
    })
    .catch(error => {
        console.error('Error approving image:', error);
        alert('Failed to approve image');
    });
}

function denyImage(imageId) {
    if (!confirm('Are you sure you want to deny this upload?')) {
        return;
    }
    
    fetch(`${serverUrl}/api/pending_images/${imageId}/deny`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadRooms();
        } else {
            alert('Failed to deny image');
        }
    })
    .catch(error => {
        console.error('Error denying image:', error);
        alert('Failed to deny image');
    });
}

// ============================================================================
// Import Rooms from CSV/XLSX
// ============================================================================

const importModal = document.getElementById('importModal');
let parsedImportData = [];

function openImportModal() {
    document.getElementById('importFileInput').value = '';
    document.getElementById('importPreview').innerHTML = '';
    document.getElementById('importStatus').innerHTML = '';
    document.getElementById('importBtn').disabled = true;
    parsedImportData = [];
    importModal.style.display = 'block';
}

function closeImportModal() {
    importModal.style.display = 'none';
    parsedImportData = [];
}

if (importModal) {
    window.addEventListener('click', function(e) {
        if (e.target === importModal) { closeImportModal(); }
    });
}

document.getElementById('importFileInput').addEventListener('change', function(e) {
    var file = e.target.files[0];
    if (!file) return;

    var ext = file.name.split('.').pop().toLowerCase();

    if (ext === 'csv') {
        var reader = new FileReader();
        reader.onload = function(ev) {
            parseCSV(ev.target.result);
        };
        reader.readAsText(file);
    } else if (ext === 'xlsx' || ext === 'xls') {
        var reader = new FileReader();
        reader.onload = function(ev) {
            parseXLSX(ev.target.result);
        };
        reader.readAsArrayBuffer(file);
    } else {
        alert('Please upload a .csv or .xlsx file');
    }
});

function parseCSV(text) {
    var lines = text.split(/\r?\n/).filter(function(l) { return l.trim(); });
    if (lines.length < 2) {
        alert('CSV must have a header row and at least one data row');
        return;
    }

    var header = lines[0].split(',').map(function(h) { return h.trim().toLowerCase().replace(/['"]/g, ''); });
    var unitIdx = header.indexOf('unit');
    var roomIdx = header.indexOf('room');
    var bedIdx = header.indexOf('bed');
    var ipIdx = header.indexOf('ipaddress');
    if (ipIdx === -1) ipIdx = header.indexOf('ip_address');
    if (ipIdx === -1) ipIdx = header.indexOf('ip');

    if (unitIdx === -1 || roomIdx === -1 || bedIdx === -1) {
        alert('CSV must have columns: unit, room, bed (ipaddress optional)');
        return;
    }

    parsedImportData = [];
    for (var i = 1; i < lines.length; i++) {
        var cols = lines[i].split(',').map(function(c) { return c.trim().replace(/['"]/g, ''); });
        if (cols[unitIdx] && cols[roomIdx] && cols[bedIdx]) {
            parsedImportData.push({
                unit: cols[unitIdx],
                room: cols[roomIdx],
                bed: cols[bedIdx],
                ipaddress: ipIdx !== -1 ? (cols[ipIdx] || '') : ''
            });
        }
    }

    showImportPreview();
}

function parseXLSX(data) {
    // Use SheetJS (XLSX) library loaded dynamically
    if (typeof XLSX === 'undefined') {
        var script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
        script.onload = function() { doParseXLSX(data); };
        script.onerror = function() { alert('Failed to load XLSX parser. Please use CSV format instead.'); };
        document.head.appendChild(script);
    } else {
        doParseXLSX(data);
    }
}

function doParseXLSX(data) {
    try {
        var workbook = XLSX.read(data, { type: 'array' });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var rows = XLSX.utils.sheet_to_json(sheet, { defval: '' });

        if (rows.length === 0) {
            alert('No data found in the spreadsheet');
            return;
        }

        // Normalize header keys to lowercase
        parsedImportData = rows.map(function(row) {
            var normalized = {};
            Object.keys(row).forEach(function(k) { normalized[k.toLowerCase().trim()] = String(row[k]).trim(); });
            return {
                unit: normalized['unit'] || '',
                room: normalized['room'] || '',
                bed: normalized['bed'] || '',
                ipaddress: normalized['ipaddress'] || normalized['ip_address'] || normalized['ip'] || ''
            };
        }).filter(function(r) { return r.unit && r.room && r.bed; });

        showImportPreview();
    } catch (err) {
        alert('Failed to parse XLSX file: ' + err.message);
    }
}

function showImportPreview() {
    var preview = document.getElementById('importPreview');
    if (parsedImportData.length === 0) {
        preview.innerHTML = '<p style="color:#dc2626;">No valid rows found. Ensure columns: unit, room, bed</p>';
        document.getElementById('importBtn').disabled = true;
        return;
    }

    var html = '<table style="width:100%; border-collapse:collapse; font-size:13px;">';
    html += '<thead><tr><th style="text-align:left; padding:6px; border-bottom:2px solid #e2e8f0;">Unit</th><th style="text-align:left; padding:6px; border-bottom:2px solid #e2e8f0;">Room</th><th style="text-align:left; padding:6px; border-bottom:2px solid #e2e8f0;">Bed</th><th style="text-align:left; padding:6px; border-bottom:2px solid #e2e8f0;">IP Address</th></tr></thead><tbody>';
    parsedImportData.forEach(function(r) {
        html += '<tr><td style="padding:4px 6px; border-bottom:1px solid #e2e8f0;">' + escapeHtml(r.unit) + '</td><td style="padding:4px 6px; border-bottom:1px solid #e2e8f0;">' + escapeHtml(r.room) + '</td><td style="padding:4px 6px; border-bottom:1px solid #e2e8f0;">' + escapeHtml(r.bed) + '</td><td style="padding:4px 6px; border-bottom:1px solid #e2e8f0;">' + escapeHtml(r.ipaddress) + '</td></tr>';
    });
    html += '</tbody></table>';
    html += '<p style="margin-top:10px; color:#64748b; font-size:13px;">' + parsedImportData.length + ' room(s) ready to import</p>';
    preview.innerHTML = html;
    document.getElementById('importBtn').disabled = false;
}

function importRooms() {
    if (parsedImportData.length === 0) return;

    var statusDiv = document.getElementById('importStatus');
    statusDiv.textContent = 'Importing...';
    statusDiv.className = 'modal-status';
    document.getElementById('importBtn').disabled = true;

    fetch(serverUrl + '/api/rooms/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rooms: parsedImportData })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.success) {
            statusDiv.textContent = 'Successfully imported ' + data.imported + ' room(s)!' + (data.skipped > 0 ? ' (' + data.skipped + ' skipped as duplicates)' : '');
            statusDiv.className = 'modal-status success';
            setTimeout(function() {
                closeImportModal();
                loadRooms();
            }, 1500);
        } else {
            statusDiv.textContent = 'Import failed: ' + (data.error || 'Unknown error');
            statusDiv.className = 'modal-status error';
            document.getElementById('importBtn').disabled = false;
        }
    })
    .catch(function(error) {
        statusDiv.textContent = 'Import failed: ' + error.message;
        statusDiv.className = 'modal-status error';
        document.getElementById('importBtn').disabled = false;
    });
}
