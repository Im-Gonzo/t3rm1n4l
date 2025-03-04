"""
Audio player implementation
"""
import os
import time
import tempfile
from threading import Thread, Event
from rich.panel import Panel
from rich.text import Text

# Try to import pygame and mutagen
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame module not found. Audio playback will be simulated.")

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("Warning: mutagen module not found. Audio metadata will be limited.")

class AudioPlayer:
    """Audio player class"""
    
    def __init__(self):
        """Initialize the audio player"""
        # Initialize pygame mixer
        self.pygame_available = PYGAME_AVAILABLE
        self.mutagen_available = MUTAGEN_AVAILABLE
        
        if self.pygame_available:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Warning: Pygame mixer initialization failed: {e}")
                self.pygame_available = False
        
        self.current_track = None
        self.is_playing = False
        self.volume = 0.7  # 0.0 to 1.0
        self.position = 0  # Current position in seconds
        self.duration = 0  # Total duration in seconds
        self.player_thread = None
        self.stop_event = Event()
        
        # Playlist management
        self.playlist = []            # List of track paths
        self.current_playlist_index = -1  # Current position in playlist
        
        # Set initial volume
        if self.pygame_available:
            pygame.mixer.music.set_volume(self.volume)
    
    def load(self, track_path):
        """Load a track into the player"""
        if not os.path.exists(track_path):
            print(f"Track not found: {track_path}")
            return False
        
        self.stop()
        self.current_track = track_path
        
        # Get metadata and duration using mutagen
        if self.mutagen_available:
            try:
                audio = MP3(track_path)
                self.duration = int(audio.info.length)
            except Exception as e:
                print(f"Error getting track info: {e}")
                self.duration = 180  # Default to 3 minutes
        else:
            # If mutagen is not available, use a default duration
            self.duration = 180  # Default to 3 minutes
        
        # Load the track with pygame if available
        try:
            if self.pygame_available:
                pygame.mixer.music.load(track_path)
            self.position = 0
            return True
        except Exception as e:
            print(f"Error loading track: {e}")
            return False
    
    def play(self):
        """Play the current track"""
        if not self.current_track:
            return False
        
        # If we're already playing, don't do anything
        if self.is_playing:
            return True
            
        try:
            # Start playback
            if self.pygame_available:
                pygame.mixer.music.play(start=self.position)
            self.is_playing = True
            
            # Start position tracking thread
            if not self.player_thread or not self.player_thread.is_alive():
                self.stop_event.clear()
                self.player_thread = Thread(target=self._playback_thread)
                self.player_thread.daemon = True
                self.player_thread.start()
                
            return True
        except Exception as e:
            print(f"Error playing track: {e}")
            return False
    
    def _playback_thread(self):
        """Thread to handle playback and position updates"""
        while not self.stop_event.is_set() and self.is_playing:
            # Update position only if we're playing
            if self.pygame_available and pygame.mixer.music.get_busy():
                # Since pygame doesn't expose exact position, we estimate
                time.sleep(0.2)  # Update 5 times per second
                self.position += 0.2
                
                # Check if track ended naturally
                if self.position >= self.duration:
                    self.position = 0
                    self.is_playing = False
                    
                    # Automatically play next track
                    self.next_track()
            else:
                # Either pygame isn't available or it isn't playing anymore
                time.sleep(0.2)  # Still update at the same rate
                
                if self.pygame_available and self.is_playing:
                    # If pygame isn't playing anymore, we've reached the end
                    self.position = 0
                    self.is_playing = False
                    
                    # Automatically play next track
                    self.next_track()
                else:
                    # If pygame isn't available, simulate playback
                    self.position += 0.2
                    if self.position >= self.duration:
                        self.position = 0
                        self.is_playing = False
                        
                        # Automatically play next track
                        self.next_track()
    
    def pause(self):
        """Pause playback"""
        if self.is_playing:
            if self.pygame_available:
                pygame.mixer.music.pause()
            self.is_playing = False
            return True
        return False
    
    def stop(self):
        """Stop playback and reset position"""
        self.stop_event.set()
        if self.pygame_available:
            pygame.mixer.music.stop()
        self.is_playing = False
        self.position = 0
    
    def toggle_play_pause(self):
        """Toggle between play and pause states"""
        # For demo purposes - try to load a sample track if none is loaded
        if not self.current_track:
            self.load_from_directory()
        
        if self.is_playing:
            self.pause()
        else:
            self.play()
        
        return self.is_playing
    
    def load_from_directory(self):
        """Load tracks from the music directory"""
        # Look for tracks in the music directory
        try:
            music_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "music")
            if os.path.exists(music_dir):
                # Collect all tracks first
                all_tracks = []
                for root, _, files in os.walk(music_dir):
                    for file in files:
                        if file.lower().endswith('.mp3'):
                            track_path = os.path.join(root, file)
                            all_tracks.append(track_path)
                
                # Set the playlist
                if all_tracks:
                    self.set_playlist(all_tracks)
                    self.next_track()
        except Exception as e:
            print(f"Error finding music files: {e}")
    
    def seek(self, position):
        """Seek to a specific position"""
        if position < 0:
            position = 0
        elif position > self.duration:
            position = self.duration
            
        was_playing = self.is_playing
        
        # Stop current playback
        if was_playing and self.pygame_available:
            pygame.mixer.music.stop()
            
        self.position = position
        
        # Restart from new position if it was playing
        if was_playing and self.pygame_available:
            pygame.mixer.music.play(start=position)
    
    def set_volume(self, volume):
        """Set player volume"""
        if volume < 0:
            volume = 0
        elif volume > 1:
            volume = 1
            
        self.volume = volume
        if self.pygame_available:
            pygame.mixer.music.set_volume(volume)
    
    def get_progress_percentage(self):
        """Get current progress as a percentage"""
        if self.duration == 0:
            return 0
        return (self.position / self.duration) * 100
    
    def format_time(self, seconds):
        """Format seconds as mm:ss"""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes}:{seconds:02d}"
    
    def get_formatted_position(self):
        """Get formatted position and duration"""
        pos = self.format_time(self.position)
        dur = self.format_time(self.duration)
        return f"{pos} / {dur}"
    
    def get_track_metadata(self):
        """Get detailed metadata for the current track"""
        if not self.current_track or not os.path.exists(self.current_track):
            return {}
        
        metadata = {
            'filename': os.path.basename(self.current_track),
            'path': self.current_track,
            'duration': self.duration,
            'bitrate': 0,
            'sample_rate': 0,
            'channels': 0,
            'has_art': False
        }
        
        # Try to extract metadata with mutagen
        if self.mutagen_available:
            try:
                # Get audio format info
                audio = MP3(self.current_track)
                metadata['bitrate'] = int(audio.info.bitrate / 1000)  # kbps
                metadata['sample_rate'] = audio.info.sample_rate / 1000  # kHz
                metadata['channels'] = audio.info.channels
                
                # Get ID3 tags
                try:
                    tags = ID3(self.current_track)
                    
                    if 'TPE1' in tags:  # Artist
                        metadata['artist'] = str(tags['TPE1'])
                    
                    if 'TIT2' in tags:  # Title
                        metadata['title'] = str(tags['TIT2'])
                    
                    if 'TALB' in tags:  # Album
                        metadata['album'] = str(tags['TALB'])
                    
                    if 'TDRC' in tags:  # Year
                        metadata['year'] = str(tags['TDRC'])
                    
                    if 'TCON' in tags:  # Genre
                        metadata['genre'] = str(tags['TCON'])
                    
                    # Check if there's album art
                    if 'APIC:' in tags or any(k.startswith('APIC:') for k in tags.keys()):
                        metadata['has_art'] = True
                        
                except ID3NoHeaderError:
                    pass
            except Exception as e:
                print(f"Error extracting metadata: {e}")
        
        return metadata
    
    def get_album_art(self):
        """Extract album art from the current track"""
        if not self.current_track or not self.mutagen_available:
            return None
        
        try:
            tags = ID3(self.current_track)
            
            # Look for the album art in APIC frames
            for k in tags.keys():
                if k.startswith('APIC:'):
                    apic = tags[k]
                    image_data = apic.data
                    mime = apic.mime
                    
                    # Write to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg' if mime == 'image/jpeg' else '.png') as temp:
                        temp.write(image_data)
                        return temp.name
                        
            return None
        except Exception as e:
            print(f"Error extracting album art: {e}")
            return None
    
    def now_playing_info(self):
        """Get information about the currently playing track"""
        if not self.current_track:
            return Panel(Text("No track loaded", style="italic"))
        
        metadata = self.get_track_metadata()
        track_name = metadata.get('title', os.path.basename(self.current_track))
        
        info = Text()
        info.append(f"Now Playing: ", style="bold green")
        info.append(f"{track_name}\n\n", style="yellow")
        
        # Add artist and album if available
        if 'artist' in metadata:
            info.append(f"Artist: {metadata['artist']}\n", style="cyan")
        if 'album' in metadata:
            info.append(f"Album: {metadata['album']}\n", style="cyan")
        
        # Show playlist position
        if self.playlist and self.current_playlist_index >= 0:
            info.append(f"Track {self.current_playlist_index + 1} of {len(self.playlist)}\n", style="magenta")
        
        # Show playback status
        status = "▶ Playing" if self.is_playing else "⏸ Paused"
        info.append(f"Status: {status}\n", style="cyan")
        info.append(f"Position: {self.get_formatted_position()}\n", style="cyan")
        info.append(f"Volume: {int(self.volume * 100)}%", style="blue")
        
        return Panel(info, title="Now Playing")
        
    def set_playlist(self, tracks):
        """Set the current playlist"""
        if not tracks:
            return False
            
        self.playlist = tracks
        self.current_playlist_index = -1
        return True
    
    def next_track(self):
        """Play next track in the playlist"""
        if not self.playlist:
            return False
            
        # Move to the next track
        if self.current_playlist_index < len(self.playlist) - 1:
            self.current_playlist_index += 1
        else:
            # Wrap around to the beginning of the playlist
            self.current_playlist_index = 0
            
        track_path = self.playlist[self.current_playlist_index]
        if self.load(track_path):
            self.play()
            return True
        else:
            # If failed to load, try the next one
            return self.next_track()
    
    def previous_track(self):
        """Play previous track in the playlist"""
        if not self.playlist:
            return False
            
        # If we're at the beginning of the current track, go to previous track
        # Otherwise, restart the current track
        if self.position < 3:  # If we're less than 3 seconds into the track
            if self.current_playlist_index > 0:
                self.current_playlist_index -= 1
            else:
                # Wrap around to the end of the playlist
                self.current_playlist_index = len(self.playlist) - 1
        else:
            # Just restart the current track
            pass
            
        track_path = self.playlist[self.current_playlist_index]
        if self.load(track_path):
            self.play()
            return True
        else:
            # If failed to load, try the previous one
            return self.previous_track()
