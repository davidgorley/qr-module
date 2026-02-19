let selectedFiles = [];

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
                window.close();
            }, 2000);
        } else {
            showStatus('Upload failed: ' + (data.error || 'Unknown error'), 'error');
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload Images';
        }
    })
    .catch(error => {
        console.error('Error uploading images:', error);
        showStatus('Upload failed: ' + error.message, 'error');
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload Images';
    });
}

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
}

document.getElementById('fileInput').addEventListener('change', function(e) {
    selectedFiles = Array.from(e.target.files);
    displayPreview();

    if (selectedFiles.length > 0) {
        document.getElementById('uploadBtn').style.display = 'block';
    }
});
