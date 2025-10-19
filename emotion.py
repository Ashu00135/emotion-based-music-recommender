from flask import Flask, render_template, request, jsonify, redirect, url_for
from fer import FER
import cv2
import base64
import os
import numpy as np
import json
from spotify_api import SpotifyAPI
from profiler import start_profiling, stop_profiling, profile_function, get_profiling_results

app = Flask(__name__)

# Initialize Spotify API
spotify_api = SpotifyAPI()

# Global profiling flag
profiling_active = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect_emotion', methods=['GET', 'POST'])
@profile_function
def detect_emotion():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        try:
            global profiling_active
            if profiling_active:
                start_profiling()
                
            # Get the image from the request
            data = request.json['image']
            img_data = base64.b64decode(data.split(',')[1])
            with open("temp_image.jpg", "wb") as f:
                f.write(img_data)

            # Load image for emotion detection
            image = cv2.imread("temp_image.jpg")
            
            # Check if image was loaded successfully
            if image is None:
                return jsonify({"error": "Failed to load image"}), 400
                
            # Initialize FER detector with MTCNN for better face detection
            # Cache the detector to avoid recreating it for each request
            if not hasattr(detect_emotion, 'detector'):
                detect_emotion.detector = FER(mtcnn=True)
            
            # Resize image for faster processing (maintaining aspect ratio)
            height, width = image.shape[:2]
            max_dimension = 480  # Limit to 480px for faster processing
            
            if max(height, width) > max_dimension:
                scale = max_dimension / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Detect emotion
            emotion, score = detect_emotion.detector.top_emotion(image)
            
            # If no face detected or emotion not recognized
            if emotion is None:
                emotion = "neutral"
                score = 0.0

            # Clean up temp file
            os.remove("temp_image.jpg")
            
            if profiling_active:
                stop_profiling()

            # Get the playlist link for the detected emotion from Spotify API
            try:
                playlist = spotify_api.get_playlist_for_emotion(emotion)
                
                # Add a flag to indicate this is a direct playlist link
                # This helps the frontend avoid React and Google Analytics errors
                return jsonify({
                    "emotion": emotion,
                    "confidence": float(score) if score else 0.0,
                    "playlist": playlist,
                    "playlist_type": "direct_link"
                })
            except Exception as e:
                print(f"Error getting Spotify playlist: {str(e)}")
                # Fallback to a curated playlist with direct embed option
                fallback_playlist = spotify_api.CURATED_PLAYLISTS.get(emotion, spotify_api.CURATED_PLAYLISTS['neutral'])
                return jsonify({
                    "emotion": emotion,
                    "confidence": float(score) if score else 0.0,
                    "playlist": fallback_playlist,
                    "playlist_type": "direct_link",
                    "error": "Could not load dynamic playlist, using fallback"
                })
                
        except Exception as e:
            print(f"Error in emotion detection: {str(e)}")
            return jsonify({"error": str(e)}), 500

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        # Get Spotify API credentials from form
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        
        # Update Spotify API with new credentials
        global spotify_api
        spotify_api = SpotifyAPI(client_id, client_secret)
        spotify_api.authenticate()
        
        # Save credentials to config file
        from spotify_api import create_spotify_config
        create_spotify_config(client_id, client_secret)
        
        return redirect(url_for('index'))
    
    return render_template('settings.html')

@app.route('/profiling', methods=['GET', 'POST'])
def profiling():
    global profiling_active
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'start':
            profiling_active = True
            return jsonify({"status": "Profiling started"})
        elif action == 'stop':
            profiling_active = False
            return jsonify({"status": "Profiling stopped"})
    
    # GET request - return profiling results and status
    results = get_profiling_results()
    return render_template('profiling.html', 
                          profiling_active=profiling_active,
                          results=results)

if __name__ == '__main__':
    # Try to authenticate with Spotify API on startup
    spotify_api.authenticate()
    app.run(debug=True, host='0.0.0.0', port=5000)
