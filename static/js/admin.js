let currentRoomId = null;
const modal = document.getElementById('uploadModal');
let allRooms = [];
let currentSort = 'created_desc';

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
                renderRooms();
                if (approvalRequired) {
                    loadPendingApprovals();
                }
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

    let filtered = allRooms.filter(r => {
        return r.name.toLowerCase().includes(search) || r.id.toLowerCase().includes(search);
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
    roomsList.innerHTML = filtered.map(room => `
        <div class="room-card ${room.enabled === 0 ? 'disabled' : ''}">
            <h3>${highlight(room.name, term)}</h3>
            <p>Room ID: <code>${highlight(room.id, term)}</code></p>
            <p class="status-indicator">
                <span class="status-badge ${room.enabled === 1 ? 'enabled' : 'disabled'}">
                    ${room.enabled === 1 ? '🟢 Enabled' : '🔴 Disabled'}
                </span>
            </p>
            <div class="room-url" onclick="copyToClipboard('${serverUrl}/display/${room.id}')">
                ${escapeHtml(`${serverUrl}/display/${room.id}`)}
            </div>
            <div class="button-group">
                <button class="btn-view" onclick="viewRoom('${room.id}')">View Display</button>
                <button class="btn-upload" onclick="openUploadModal('${room.id}', '${escapeHtml(room.name)}')">Upload Images</button>
                <button class="btn-toggle ${room.enabled === 1 ? 'btn-disable' : 'btn-enable'}" onclick="toggleRoom('${room.id}')">
                    ${room.enabled === 1 ? 'Disable' : 'Enable'}
                </button>
                <button class="btn-clear" onclick="clearRoomImages('${room.id}')">Clear</button>
                <button class="btn-delete" onclick="deleteRoom('${room.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

function createRoom() {
    const roomName = document.getElementById('roomName').value.trim();

    if (!roomName) {
        alert('Please enter a room name');
        return;
    }

    fetch(`${serverUrl}/api/rooms`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: roomName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('roomName').value = '';
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
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadRooms();
        } else {
            console.error('Failed to clear images');
        }
    })
    .catch(error => {
        console.error('Error clearing images:', error);
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

document.getElementById('roomName').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        createRoom();
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

loadRooms();

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
