# Emotion Recognition with Spotify Playlist Recommendations

A web application that detects emotions from facial expressions and recommends Spotify playlists to match your mood.

## Features

- **Real-time Emotion Detection**: Analyze facial expressions from webcam or uploaded images
- **Spotify Integration**: Get personalized playlist recommendations based on your detected emotion
- **Performance Profiling**: Built-in profiling dashboard to monitor application performance
- **Responsive UI**: Modern, user-friendly interface that works on various devices

## Screenshots

### Main Interface
![Main Interface](https://i.imgur.com/placeholder1.jpg)
*Replace with actual screenshot of your application's main interface*

### Emotion Detection Results
![Emotion Detection](https://i.imgur.com/placeholder2.jpg)
*Replace with actual screenshot of emotion detection results*

### Profiling Dashboard
![Profiling Dashboard](https://i.imgur.com/placeholder3.jpg)
*Replace with actual screenshot of the profiling dashboard*

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/emotion-recognition.git
cd emotion-recognition
```

2. Install the required dependencies:
```
pip install flask fer==22.4.0 moviepy requests
```

3. Set up Spotify API credentials:
   - Create a Spotify Developer account at [developer.spotify.com](https://developer.spotify.com)
   - Create a new application to get your Client ID and Client Secret
   - Add these credentials in the application's settings page

## Usage

1. Start the application:
```
python emotion.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Use the application:
   - Allow camera access for webcam emotion detection
   - Capture an image or upload one from your device
   - View your detected emotion and recommended Spotify playlist
   - Click "Open in Spotify" to listen to the recommended playlist

## Performance Optimization

The application includes built-in performance profiling:

1. Access the profiling dashboard at:
```
http://localhost:5000/profiling
```

2. Start profiling to analyze application performance
3. View detailed statistics on function execution times and resource usage

## Project Structure

- `emotion.py`: Main Flask application
- `spotify_api.py`: Spotify API integration
- `profiler.py`: Performance profiling utilities
- `templates/`: HTML templates
- `static/`: JavaScript and CSS files

## Technologies Used

- **Backend**: Python, Flask
- **Emotion Detection**: FER (Facial Emotion Recognition)
- **Music Recommendations**: Spotify API
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Performance**: cProfile, pstats

## License

[MIT License](LICENSE)

## Acknowledgments

- FER library for emotion detection
- Spotify API for music recommendations
- Flask framework for web application development