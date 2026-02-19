let currentImageIndex = 0;
let images = [];
let slideshowInterval = null;
let isShowingImages = false;

function generateQRCode() {
    const qrDiv = document.getElementById('qrcode');
    const uploadUrl = `${serverUrl}/upload/${roomId}`;
    qrDiv.innerHTML = '';

    new QRCode(qrDiv, {
        text: uploadUrl,
        width: 300,
        height: 300,
        colorDark: '#000000',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
    });
}

function checkForImages() {
    fetch(`${serverUrl}/api/get_images/${roomId}`)
        .then(response => response.json())
        .then(data => {
            if (data.images && data.images.length > 0) {
                if (!isShowingImages) {
                    images = data.images;
                    showImages();
                }
            } else {
                if (isShowingImages) {
                    showQRCode();
                }
            }
        })
        .catch(error => {
            console.error('Error checking for images:', error);
        });
}

function showQRCode() {
    isShowingImages = false;
    document.getElementById('imageContainer').style.display = 'none';
    document.getElementById('qrContainer').style.display = 'flex';
    stopSlideshow();
}

function showImages() {
    isShowingImages = true;
    document.getElementById('qrContainer').style.display = 'none';
    document.getElementById('imageContainer').style.display = 'flex';
    currentImageIndex = 0;
    displayCurrentImage();

    if (images.length > 1) {
        startSlideshow();
    } else {
        stopSlideshow();
    }
}

function displayCurrentImage() {
    const img = document.getElementById('displayImage');
    img.src = images[currentImageIndex];
}

function startSlideshow() {
    stopSlideshow();
    slideshowInterval = setInterval(() => {
        currentImageIndex = (currentImageIndex + 1) % images.length;
        displayCurrentImage();
    }, slideDuration);
}

function stopSlideshow() {
    if (slideshowInterval) {
        clearInterval(slideshowInterval);
        slideshowInterval = null;
    }
}

function clearImages() {
    fetch(`${serverUrl}/api/clear_images/${roomId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            images = [];
            isShowingImages = false;
            stopSlideshow();
            showQRCode();
        } else {
            console.error('Failed to clear images');
        }
    })
    .catch(error => {
        console.error('Error clearing images:', error);
    });
}

generateQRCode();
checkForImages();
setInterval(checkForImages, 3000);

// Bind clear button event listener (works better on touch devices than inline onclick)
document.getElementById('clearBtn').addEventListener('click', clearImages);
