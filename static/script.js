// Global variables
let video = null;
let canvas = null;
let capturedImage = null;
let streaming = false;

// Initialize webcam when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Initialize webcam
    initWebcam();
    
    // Set up event listeners
    document.getElementById('capture-btn').addEventListener('click', captureImage);
    document.getElementById('detect-emotion-btn').addEventListener('click', detectEmotionFromWebcam);
    document.getElementById('uploadForm').addEventListener('submit', handleImageUpload);
    
    // Initialize tabs
    const tabEls = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabEls.forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', event => {
            if (event.target.id === 'webcam-tab' && !streaming) {
                initWebcam();
            }
        });
    });
});

// Initialize webcam
function initWebcam() {
    video = document.getElementById('webcam');
    canvas = document.getElementById('snapshot');
    
    // Get user media
    navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        .then(stream => {
            video.srcObject = stream;
            video.play();
            streaming = true;
        })
        .catch(err => {
            console.error("Error accessing webcam:", err);
            alert("Error accessing webcam. Please make sure your camera is connected and permissions are granted.");
        });
    
    // Set canvas size when video metadata is loaded
    video.addEventListener('loadedmetadata', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
    });
}

// Capture image from webcam
function captureImage() {
    if (!streaming) return;
    
    const context = canvas.getContext('2d');
    
    // Draw the video frame to the canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Get the image data as base64
    capturedImage = canvas.toDataURL('image/jpeg');
    
    // Show the snapshot and enable the detect button
    document.getElementById('snapshot-container').style.display = 'block';
    document.getElementById('detect-emotion-btn').disabled = false;
}

// Detect emotion from webcam image
async function detectEmotionFromWebcam() {
    if (!capturedImage) return;
    
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.querySelector('.loading');
    
    // Show loading indicator
    loadingDiv.style.display = 'block';
    resultDiv.style.display = 'none';
    
    try {
        // Send the image to the backend
        const response = await fetch("/detect_emotion", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ image: capturedImage }),
        });

        const data = await response.json();
        
        // Hide loading indicator
        loadingDiv.style.display = 'none';
        
        if (response.ok) {
            // Display the result
            resultDiv.innerHTML = createResultHTML(data);
            resultDiv.style.display = 'block';
            
            // Add event listener for play button if it exists
            const playButton = document.getElementById('play-button');
            if (playButton) {
                playButton.addEventListener('click', () => {
                    window.open(data.playlist, '_blank');
                });
            }
        } else {
            resultDiv.innerHTML = `<p class="text-danger">Error: ${data.error}</p>`;
            resultDiv.style.display = 'block';
        }
    } catch (error) {
        console.error("Error:", error);
        loadingDiv.style.display = 'none';
        resultDiv.innerHTML = `<p class="text-danger">Error: Unable to process your request.</p>`;
        resultDiv.style.display = 'block';
    }
}

// Handle image upload
async function handleImageUpload(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById("imageUpload");
    const resultDiv = document.getElementById("result");
    const loadingDiv = document.querySelector('.loading');

    if (!fileInput.files[0]) {
        alert("Please upload an image!");
        return;
    }

    // Show loading indicator
    loadingDiv.style.display = 'block';
    resultDiv.style.display = 'none';

    const file = fileInput.files[0];
    const reader = new FileReader();

    // Read the file as Base64
    reader.onload = async (e) => {
        const base64Image = e.target.result;

        try {
            // Send the image to the backend
            const response = await fetch("/detect_emotion", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ image: base64Image }),
            });

            const data = await response.json();
            
            // Hide loading indicator
            loadingDiv.style.display = 'none';
            
            if (response.ok) {
                // Display the result
                resultDiv.innerHTML = createResultHTML(data);
                resultDiv.style.display = 'block';
                
                // Add event listener for play button if it exists
                const playButton = document.getElementById('play-button');
                if (playButton) {
                    playButton.addEventListener('click', () => {
                        window.open(data.playlist, '_blank');
                    });
                }
            } else {
                resultDiv.innerHTML = `<p class="text-danger">Error: ${data.error}</p>`;
                resultDiv.style.display = 'block';
            }
        } catch (error) {
            console.error("Error:", error);
            loadingDiv.style.display = 'none';
            resultDiv.innerHTML = `<p class="text-danger">Error: Unable to process your request.</p>`;
            resultDiv.style.display = 'block';
        }
    };

    reader.readAsDataURL(file);
}

// Create HTML for result display
function createResultHTML(data) {
    // Get emoji based on emotion
    const emoji = getEmotionEmoji(data.emotion);
    
    // Format playlist name
    const playlistName = formatPlaylistName(data.playlist);
    
    // Check if there was an error with the playlist
    const errorMessage = data.error ? 
        `<p class="text-warning small">${data.error}</p>` : '';
    
    return `
        <div class="emotion-display">
            <span class="emotion-emoji">${emoji}</span>
            <span class="emotion-text">You're feeling <strong>${data.emotion}</strong></span>
        </div>
        <div class="playlist-container">
            <p>Here's a playlist that matches your mood:</p>
            ${errorMessage}
            <div class="d-flex justify-content-center align-items-center">
                <a href="${data.playlist}" target="_blank" class="playlist-link">${playlistName}</a>
                <button id="play-button" class="btn btn-success ms-3">
                    <i class="fas fa-play"></i> Play
                </button>
            </div>
            <div class="spotify-embed mt-3">
                <!-- Use a direct link button instead of an embed to avoid React errors -->
                <div class="text-center mb-3">
                    <a href="${data.playlist}" target="_blank" class="btn btn-lg btn-outline-success">
                        <i class="fas fa-external-link-alt"></i> Open in Spotify
                    </a>
                </div>
            </div>
        </div>
    `;
}

// Get emoji based on emotion
function getEmotionEmoji(emotion) {
    const emojis = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'neutral': '😐',
        'surprise': '😲',
        'fear': '😨',
        'disgust': '🤢'
    };
    
    return emojis[emotion] || '🎵';
}

// Format playlist name from URL
function formatPlaylistName(url) {
    // Extract playlist name from URL or use default
    if (url.includes('playlist')) {
        const parts = url.split('/');
        const lastPart = parts[parts.length - 1];
        
        // Try to make it more readable
        if (lastPart.includes('_playlist_link')) {
            return lastPart.replace('_playlist_link', ' Playlist').replace(/_/g, ' ');
        }
        
        return lastPart;
    }
    
    return "Spotify Playlist";
}
