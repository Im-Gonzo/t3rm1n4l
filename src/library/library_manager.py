"""
Library management implementation
"""
import os
import json
import glob
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class Track:
    """Represents a music track"""
    path: str
    title: str
    artist: str = "Unknown Artist"
    album: str = "Unknown Album"
    duration: int = 0  # Duration in seconds
    
    @property
    def formatted_duration(self) -> str:
        """Format duration as mm:ss"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"


@dataclass
class Playlist:
    """Represents a playlist of tracks"""
    name: str
    tracks: List[str]  # List of track paths


class LibraryManager:
    """Manages the music library"""
    
    def __init__(self, library_path: Optional[str] = None):
        """Initialize the library manager"""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self.library_file = os.path.join(self.data_dir, "library.json")
        self.playlists_dir = os.path.join(self.data_dir, "playlists")
        
        # Make sure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.playlists_dir, exist_ok=True)
        
        # Set music library path
        if library_path:
            self.library_path = library_path
        else:
            # Use default music directory from utils.helpers
            from src.utils.helpers import find_music_directory
            self.library_path = find_music_directory() or os.path.join(self.data_dir, "music")
            
        # Initialize tracks and playlists dictionaries
        self.tracks: Dict[str, Track] = {}
        self.playlists: Dict[str, Playlist] = {}
        
        # Load existing library first
        self.load_library()
        
        # Scan for music files on startup
        self.scan_library()
            
        # Create music directory if it doesn't exist
        os.makedirs(self.library_path, exist_ok=True)
    
    def load_library(self):
        """Load the library from the library file"""
        if os.path.exists(self.library_file):
            try:
                with open(self.library_file, 'r') as f:
                    data = json.load(f)
                    
                for track_data in data.get('tracks', []):
                    track = Track(**track_data)
                    self.tracks[track.path] = track
                    
                # Load playlists from their individual files
                self.load_playlists()
            except Exception as e:
                print(f"Error loading library: {e}")
                # Create empty library if loading fails
                self.tracks = {}
                self.playlists = {}
        
    def save_library(self):
        """Save the library to the library file"""
        try:
            data = {
                'tracks': [asdict(track) for track in self.tracks.values()]
            }
            
            with open(self.library_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            # Save playlists to their individual files
            self.save_playlists()
        except Exception as e:
            print(f"Error saving library: {e}")
    
    def load_playlists(self):
        """Load playlists from the playlists directory"""
        self.playlists = {}
        playlist_files = glob.glob(os.path.join(self.playlists_dir, "*.json"))
        
        for playlist_file in playlist_files:
            try:
                with open(playlist_file, 'r') as f:
                    data = json.load(f)
                    name = data.get('name', Path(playlist_file).stem)
                    tracks = data.get('tracks', [])
                    self.playlists[name] = Playlist(name=name, tracks=tracks)
            except Exception as e:
                print(f"Error loading playlist {playlist_file}: {e}")
    
    def save_playlists(self):
        """Save playlists to their individual files"""
        for name, playlist in self.playlists.items():
            try:
                playlist_file = os.path.join(self.playlists_dir, f"{name}.json")
                with open(playlist_file, 'w') as f:
                    json.dump(asdict(playlist), f, indent=2)
            except Exception as e:
                print(f"Error saving playlist {name}: {e}")
    
    def scan_library(self):
        """Scan the music directory for audio files"""
        print(f"Scanning music directory: {self.library_path}")
        if not os.path.exists(self.library_path):
            print(f"Music directory does not exist: {self.library_path}")
            return
            
        supported_extensions = [".mp3", ".wav", ".ogg", ".flac"]
        found_tracks = []
        
        try:
            for root, _, files in os.walk(self.library_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in supported_extensions):
                        path = os.path.join(root, file)
                        found_tracks.append(path)
            
            print(f"Found {len(found_tracks)} audio files")
            if found_tracks:
                self.add_tracks(found_tracks)
        except Exception as e:
            print(f"Error scanning music directory: {e}")

    def add_tracks(self, paths: List[str]):
        """Add tracks to the library"""
        for path in paths:
            if not os.path.exists(path):
                print(f"File not found: {path}")
                continue
                
            # Try to get metadata using mutagen
            try:
                try:
                    from mutagen.mp3 import MP3
                    from mutagen.id3 import ID3, ID3NoHeaderError
                    
                    audio = MP3(path)
                    duration = int(audio.info.length)
                    
                    try:
                        id3 = ID3(path)
                        artist = str(id3.get('TPE1', 'Unknown Artist'))
                        title = str(id3.get('TIT2', os.path.basename(path)))
                        album = str(id3.get('TALB', 'Unknown Album'))
                    except ID3NoHeaderError:
                        # If no ID3 tags, extract from filename
                        from src.utils.helpers import extract_track_info_from_filename
                        info = extract_track_info_from_filename(os.path.basename(path))
                        artist = info['artist']
                        title = info['title']
                        album = 'Unknown Album'
                except ImportError:
                    # Mutagen not installed, use filename info
                    print("Mutagen not available, using filename for track info")
                    from src.utils.helpers import extract_track_info_from_filename
                    info = extract_track_info_from_filename(os.path.basename(path))
                    artist = info['artist']
                    title = info['title']
                    album = 'Unknown Album'
                    duration = 180  # Default duration
                
            except Exception as e:
                # Fall back to filename parsing
                from src.utils.helpers import extract_track_info_from_filename
                info = extract_track_info_from_filename(os.path.basename(path))
                artist = info['artist']
                title = info['title']
                album = 'Unknown Album'
                duration = 180  # Default duration
                
            track = Track(
                path=path,
                title=title,
                artist=artist,
                album=album,
                duration=duration
            )
            
            self.tracks[path] = track
        
        self.save_library()
    
    def remove_track(self, path: str):
        """Remove a track from the library"""
        if path in self.tracks:
            del self.tracks[path]
            
            # Also remove from any playlists
            for playlist in self.playlists.values():
                if path in playlist.tracks:
                    playlist.tracks.remove(path)
            
            self.save_library()
    
    def create_playlist(self, name: str):
        """Create a new playlist"""
        if name in self.playlists:
            return False
        
        self.playlists[name] = Playlist(name=name, tracks=[])
        self.save_playlists()
        return True
    
    def add_to_playlist(self, playlist_name: str, track_paths: List[str]):
        """Add tracks to a playlist"""
        if playlist_name not in self.playlists:
            return False
        
        for path in track_paths:
            if path in self.tracks and path not in self.playlists[playlist_name].tracks:
                self.playlists[playlist_name].tracks.append(path)
        
        self.save_playlists()
        return True
    
    def remove_from_playlist(self, playlist_name: str, track_path: str):
        """Remove a track from a playlist"""
        if playlist_name not in self.playlists:
            return False
        
        if track_path in self.playlists[playlist_name].tracks:
            self.playlists[playlist_name].tracks.remove(track_path)
            self.save_playlists()
            return True
        
        return False
    
    def delete_playlist(self, name: str):
        """Delete a playlist"""
        if name in self.playlists:
            del self.playlists[name]
            
            # Also delete the playlist file
            playlist_file = os.path.join(self.playlists_dir, f"{name}.json")
            if os.path.exists(playlist_file):
                os.remove(playlist_file)
            
            return True
        
        return False
    
    def get_all_tracks(self) -> List[Track]:
        """Get all tracks in the library"""
        return list(self.tracks.values())
    
    def get_track(self, path: str) -> Optional[Track]:
        """Get a track by path"""
        return self.tracks.get(path)
    
    def get_all_playlists(self) -> List[str]:
        """Get all playlist names"""
        return list(self.playlists.keys())
    
    def get_playlist_tracks(self, name: str) -> List[Track]:
        """Get all tracks in a playlist"""
        if name not in self.playlists:
            return []
        
        tracks = []
        for path in self.playlists[name].tracks:
            if path in self.tracks:
                tracks.append(self.tracks[path])
        
        return tracks
    
    def search(self, query: str) -> List[Track]:
        """Search for tracks by name, artist, or album"""
        query = query.lower()
        results = []
        
        for track in self.tracks.values():
            if (query in track.title.lower() or
                query in track.artist.lower() or
                query in track.album.lower()):
                results.append(track)
        
        return results
        
    def get_artists(self):
        """Get a list of all artists in the library"""
        artists = set(track.artist for track in self.tracks.values())
        return sorted(list(artists))
    
    def get_tracks_by_artist(self, artist):
        """Get all tracks by a specific artist"""
        return [track for track in self.tracks.values() if track.artist == artist]
    
    def get_albums(self):
        """Get a list of all albums in the library"""
        albums = set(track.album for track in self.tracks.values() if track.album != "Unknown Album")
        return sorted(list(albums))
    
    def get_tracks_by_album(self, album):
        """Get all tracks from a specific album"""
        return [track for track in self.tracks.values() if track.album == album]
