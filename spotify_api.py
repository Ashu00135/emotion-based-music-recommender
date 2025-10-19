import os
import json
import base64
import requests
import time
import functools
from urllib.parse import urlencode

class SpotifyAPI:
    """
    Spotify API wrapper for authentication and playlist recommendations
    """
    
    # Spotify API endpoints
    AUTH_URL = 'https://accounts.spotify.com/api/token'
    BASE_URL = 'https://api.spotify.com/v1/'
    
    # Emotion to genre mapping
    EMOTION_TO_GENRE = {
        'happy': ['happy', 'pop', 'dance', 'party'],
        'sad': ['sad', 'chill', 'acoustic', 'melancholy'],
        'angry': ['rock', 'metal', 'intense', 'aggressive'],
        'neutral': ['indie', 'alternative', 'ambient', 'focus'],
        'surprise': ['electronic', 'experimental', 'upbeat', 'energetic'],
        'fear': ['ambient', 'soundtrack', 'instrumental', 'cinematic'],
        'disgust': ['punk', 'grunge', 'heavy', 'dark']
    }
    
    # Curated playlists for each emotion (fallback if API fails)
    CURATED_PLAYLISTS = {
        'happy': 'https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC',  # Happy Hits
        'sad': 'https://open.spotify.com/playlist/37i9dQZF1DX7qK8ma5wgG1',    # Sad Songs
        'angry': 'https://open.spotify.com/playlist/37i9dQZF1DX4eRPd9frC1m',  # Rage Beats
        'neutral': 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO', # Peaceful Piano
        'surprise': 'https://open.spotify.com/playlist/37i9dQZF1DX6GwdWRQMQpq', # Discover Weekly
        'fear': 'https://open.spotify.com/playlist/37i9dQZF1DX6msyQisGtxK',    # Cinematic Chillout
        'disgust': 'https://open.spotify.com/playlist/37i9dQZF1DX9wa6XirBPv8'  # Dark & Stormy
    }
    
    def __init__(self, client_id=None, client_secret=None):
        """Initialize with client credentials"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        
        # Try to load credentials from config file if not provided
        if not client_id or not client_secret:
            self._load_credentials()
    
    def _load_credentials(self):
        """Load Spotify API credentials from config file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.client_id = config.get('spotify_client_id')
                    self.client_secret = config.get('spotify_client_secret')
        except Exception as e:
            print(f"Error loading Spotify credentials: {e}")
    
    def authenticate(self):
        """Get Spotify access token using client credentials flow"""
        if not self.client_id or not self.client_secret:
            print("Spotify API credentials not found")
            return False
            
        try:
            # Encode client ID and secret for authorization header
            auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            
            # Make POST request to get access token
            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(self.AUTH_URL, headers=headers, data=data)
            response_data = response.json()
            
            if response.status_code == 200:
                self.access_token = response_data['access_token']
                return True
            else:
                print(f"Authentication error: {response_data.get('error')}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    # Cache playlist results for 1 hour to improve performance
    @functools.lru_cache(maxsize=32)
    def get_playlist_for_emotion(self, emotion):
        """Get a playlist recommendation based on detected emotion"""
        # If no emotion detected or invalid emotion, return default playlist
        if not emotion or emotion not in self.EMOTION_TO_GENRE:
            return self.CURATED_PLAYLISTS.get('neutral')
        
        # If no API credentials or authentication fails, return curated playlist
        if not self.access_token and not self.authenticate():
            return self.CURATED_PLAYLISTS.get(emotion)
        
        try:
            # Get genres for the detected emotion
            genres = self.EMOTION_TO_GENRE.get(emotion, ['pop'])
            
            # Search for playlists matching the emotion
            headers = {'Authorization': f'Bearer {self.access_token}'}
            search_query = f"{emotion} {genres[0]}"
            
            params = {
                'q': search_query,
                'type': 'playlist',
                'limit': 5
            }
            
            endpoint = f"{self.BASE_URL}search"
            response = requests.get(endpoint, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                playlists = data.get('playlists', {}).get('items', [])
                
                if playlists:
                    # Return the first playlist URL
                    return playlists[0]['external_urls']['spotify']
            
            # Fallback to curated playlist if API request fails or no results
            return self.CURATED_PLAYLISTS.get(emotion)
            
        except requests.exceptions.RequestException as e:
            print(f"Network error getting playlist: {e}")
            return self.CURATED_PLAYLISTS.get(emotion)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self.CURATED_PLAYLISTS.get(emotion)
        except Exception as e:
            print(f"Error getting playlist: {e}")
            return self.CURATED_PLAYLISTS.get(emotion)

# Helper function to create config file with Spotify credentials
def create_spotify_config(client_id, client_secret):
    """Create or update config file with Spotify API credentials"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    # Load existing config if it exists
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except:
            pass
    
    # Update with Spotify credentials
    config['spotify_client_id'] = client_id
    config['spotify_client_secret'] = client_secret
    
    # Save config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)