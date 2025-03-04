"""
UI components for the terminal music player
"""
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
from rich.box import ROUNDED
import os
from datetime import datetime

class PlayerControls:
    """UI component for player controls"""
    
    def __init__(self, player):
        """Initialize with a reference to the audio player"""
        self.player = player
    
    def render(self):
        """Render the player controls"""
        controls = Text()
        controls.append("⏮️  ", style="cyan")
        
        if self.player.is_playing:
            controls.append("⏸️  ", style="yellow bold")
        else:
            controls.append("▶️  ", style="green bold")
            
        controls.append("⏭️  ", style="cyan")
        controls.append("   ")
        controls.append("🔊 ", style="blue")
        controls.append("   ")
        controls.append("🔍 ", style="magenta")
        
        help_text = "[Space]=Play/Pause [</>]=Prev/Next [+/-]=Volume [Tab]=Switch Panel [↑/↓]=Navigate [Enter]=Select [q]=Quit"
        return Panel(
            Align.center(controls),
            title="Controls",
            subtitle=help_text,
            border_style="blue"
        )


class ArtistView:
    """UI component for artists list view"""
    
    def __init__(self, library):
        """Initialize with a reference to the library manager"""
        self.library = library
        self.selected_index = 0
        self.artists = []
        self.update_artists()
    
    def update_artists(self):
        """Update the list of artists from the library"""
        # Get all unique artists from the library
        tracks = self.library.get_all_tracks()
        artists = set()
        for track in tracks:
            artists.add(track.artist)
        
        self.artists = sorted(list(artists))
        if self.artists and self.selected_index >= len(self.artists):
            self.selected_index = len(self.artists) - 1
    
    def render(self, selected_artist=None):
        """Render the artists list"""
        self.update_artists()
        
        table = Table(expand=True, box=ROUNDED, padding=(0, 1, 0, 1))
        table.add_column("Artists", style="cyan")
        
        if not self.artists:
            table.add_row("No artists found")
        else:
            for i, artist in enumerate(self.artists):
                if i == self.selected_index:
                    table.add_row(f"[bold yellow]> {artist}")
                else:
                    table.add_row(artist)
        
        return Panel(
            table,
            title="Artists",
            border_style="green"
        )
    
    def select_next(self):
        """Select the next artist in the list"""
        if self.artists and self.selected_index < len(self.artists) - 1:
            self.selected_index += 1
    
    def select_prev(self):
        """Select the previous artist in the list"""
        if self.artists and self.selected_index > 0:
            self.selected_index -= 1
    
    def get_selected_artist(self):
        """Get the currently selected artist"""
        if self.artists and 0 <= self.selected_index < len(self.artists):
            return self.artists[self.selected_index]
        return None


class SongView:
    """UI component for songs list view"""
    
    def __init__(self, library, player):
        """Initialize with references to the library manager and player"""
        self.library = library
        self.player = player
        self.selected_index = 0
        self.songs = []
    
    def update_songs(self, artist=None):
        """Update the list of songs, optionally filtered by artist"""
        tracks = self.library.get_all_tracks()
        
        # Filter tracks by artist if specified
        if artist:
            tracks = [t for t in tracks if t.artist == artist]
        
        # Sort by title
        tracks.sort(key=lambda t: t.title)
        self.songs = tracks
        
        # Adjust selected index if needed
        if self.songs and self.selected_index >= len(self.songs):
            self.selected_index = len(self.songs) - 1
        elif not self.songs:
            self.selected_index = 0
    
    def render(self, artist=None, selected_song=None):
        """Render the songs list"""
        self.update_songs(artist)
        
        table = Table(expand=True, box=ROUNDED, padding=(0, 1, 0, 1))
        table.add_column("Title", style="cyan")
        table.add_column("Duration", justify="right", style="blue", width=8)
        
        if not self.songs:
            table.add_row("No songs found", "")
        else:
            for i, track in enumerate(self.songs):
                if i == self.selected_index:
                    # Currently playing indicator
                    now_playing = ""
                    if self.player.current_track and os.path.basename(self.player.current_track) == os.path.basename(track.path):
                        now_playing = "🎵 "
                    
                    table.add_row(
                        f"[bold yellow]> {now_playing}{track.title}",
                        f"[bold yellow]{track.formatted_duration}"
                    )
                else:
                    # Currently playing indicator
                    now_playing = ""
                    if self.player.current_track and os.path.basename(self.player.current_track) == os.path.basename(track.path):
                        now_playing = "🎵 "
                    
                    table.add_row(f"{now_playing}{track.title}", track.formatted_duration)
        
        return Panel(
            table,
            title="Songs",
            border_style="cyan"
        )
    
    def select_next(self):
        """Select the next song in the list"""
        if self.songs and self.selected_index < len(self.songs) - 1:
            self.selected_index += 1
    
    def select_prev(self):
        """Select the previous song in the list"""
        if self.songs and self.selected_index > 0:
            self.selected_index -= 1
    
    def get_selected_song(self):
        """Get the currently selected song"""
        if self.songs and 0 <= self.selected_index < len(self.songs):
            return self.songs[self.selected_index].path
        return None


class DetailsView:
    """UI component for song details view"""
    
    def __init__(self, player):
        """Initialize with a reference to the audio player"""
        self.player = player
    
    def render(self):
        """Render the song details"""
        if not self.player.current_track:
            return Panel(
                Text("No track loaded", style="italic"),
                title="Track Details",
                border_style="magenta"
            )
        
        # Track info and metadata
        info = Text()
        
        # Show progress bar
        progress = Progress(
            TextColumn("[blue]{task.description}"),
            BarColumn(complete_style="green"),
            TextColumn("[cyan]{task.percentage:.0f}%"),
            TextColumn("[yellow]{task.fields[time]}")
        )
        
        # Get progress info
        status = "Playing" if self.player.is_playing else "Paused"
        percentage = self.player.get_progress_percentage()
        time_info = self.player.get_formatted_position()
        
        # Add progress task
        task = progress.add_task(status, total=100, time=time_info)
        progress.update(task, completed=percentage)
        
        # Album art placeholder (if available)
        try:
            from mutagen.id3 import ID3
            from mutagen.mp3 import MP3
            
            # Get basic track info
            track_name = os.path.basename(self.player.current_track)
            info.append(f"Now Playing: ", style="bold green")
            info.append(f"{track_name}\n\n", style="yellow")
            
            audio = MP3(self.player.current_track)
            
            # Show audio format info
            info.append(f"Format: MP3\n", style="cyan")
            info.append(f"Bitrate: {int(audio.info.bitrate / 1000)} kbps\n", style="cyan")
            info.append(f"Sample Rate: {audio.info.sample_rate / 1000} kHz\n", style="cyan")
            info.append(f"Channels: {audio.info.channels}\n", style="cyan")
            
            # Get ID3 tags if available
            try:
                tags = ID3(self.player.current_track)
                
                if 'TALB' in tags:
                    info.append(f"\nAlbum: {str(tags['TALB'])}\n", style="cyan")
                
                if 'TDRC' in tags:  # Recording date
                    info.append(f"Year: {str(tags['TDRC'])}\n", style="cyan")
                
                if 'TCON' in tags:  # Genre
                    info.append(f"Genre: {str(tags['TCON'])}\n", style="cyan")
                
                # Check if there's album art
                if 'APIC:' in tags:
                    info.append("\n[Album art is available but can't be displayed in the terminal]\n", style="yellow")
            except:
                pass
                
        except Exception as e:
            # If metadata extraction fails, show basic info
            track_name = os.path.basename(self.player.current_track)
            info.append(f"Now Playing: ", style="bold green")
            info.append(f"{track_name}\n", style="yellow")
        
        # Volume control
        volume_text = Text(f"\nVolume: {int(self.player.volume * 100)}%", style="blue")
        
        # Combine elements
        details = Text()
        details.append_text(info)
        details.append("\n")
        details.append_text(volume_text)
        
        return Panel(
            details,
            title="Track Details",
            footer=progress,
            border_style="magenta"
        )