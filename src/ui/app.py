import select
import termios
import tty
import sys
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.live import Live

from src.player.player import AudioPlayer
from src.library.library_manager import LibraryManager
from src.ui.components import PlayerControls, ArtistView, SongView, DetailsView

# Try to import keyboard for better input handling
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Keyboard module not available. Using fallback input handling.")

class TerminalApp:
    """Main terminal application class"""
    
    def __init__(self):
        """Initialize the terminal application"""
        self.console = Console()
        self.player = AudioPlayer()
        self.library = LibraryManager()
        self.running = False
        self.setup_ui()
        
        # Initialize state for artist/song selection
        self.selected_artist = None
        self.selected_song = None
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set a fixed size for the terminal
        self.width = 120
        self.height = 36
        
        self.layout = Layout(size=(self.height, self.width))
        
        # Create header, main content, and footer sections
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Split main content into 3 columns
        self.layout["main"].split_row(
            Layout(name="artists", ratio=1),
            Layout(name="songs", ratio=1),
            Layout(name="details", ratio=1)
        )
        
        # Create UI components
        self.controls = PlayerControls(self.player)
        self.artist_view = ArtistView(self.library)
        self.song_view = SongView(self.library, self.player)
        self.details_view = DetailsView(self.player)
        
        # Add a status message that updates based on actions
        self.status_message = "Welcome to t3rm1n4l music player"
    
    def render(self):
        """Render the UI"""
        # Render header with title
        self.layout["header"].update(Panel(
            Text("t3rm1n4l", style="bold green", justify="center"),
            subtitle=self.status_message
        ))
        
        # Render the three main panels
        self.layout["artists"].update(self.artist_view.render(self.selected_artist))
        self.layout["songs"].update(self.song_view.render(self.selected_artist, self.selected_song))
        self.layout["details"].update(self.details_view.render())
        
        # Render footer with controls
        self.layout["footer"].update(self.controls.render())
        
        return self.layout
    
    def toggle_play_pause(self):
        """Toggle play/pause"""
        self.player.toggle_play_pause()
        if self.player.is_playing:
            self.status_message = "Playing"
        else:
            self.status_message = "Paused"
    
    def next_track(self):
        """Play next track"""
        if self.player.next_track():
            self.status_message = "Playing next track"
        else:
            self.status_message = "No more tracks"
    
    def previous_track(self):
        """Play previous track"""
        if self.player.previous_track():
            self.status_message = "Playing previous track"
        else:
            self.status_message = "No previous tracks"
    
    def select_next_artist(self):
        """Select the next artist in the list"""
        self.artist_view.select_next()
        self.selected_artist = self.artist_view.get_selected_artist()
        self.selected_song = None
        self.status_message = f"Selected artist: {self.selected_artist}"
    
    def select_prev_artist(self):
        """Select the previous artist in the list"""
        self.artist_view.select_prev()
        self.selected_artist = self.artist_view.get_selected_artist()
        self.selected_song = None
        self.status_message = f"Selected artist: {self.selected_artist}"
    
    def select_next_song(self):
        """Select the next song in the list"""
        self.song_view.select_next()
        self.selected_song = self.song_view.get_selected_song()
        self.status_message = f"Selected song: {self.selected_song}"
    
    def select_prev_song(self):
        """Select the previous song in the list"""
        self.song_view.select_prev()
        self.selected_song = self.song_view.get_selected_song()
        self.status_message = f"Selected song: {self.selected_song}"
    
    def play_selected_song(self):
        """Play the currently selected song"""
        if self.selected_song:
            if self.player.load(self.selected_song):
                self.player.play()
                self.status_message = f"Playing: {self.selected_song}"
            else:
                self.status_message = f"Failed to load: {self.selected_song}"
    
    def quit(self):
        """Quit the application"""
        self.running = False
        self.status_message = "Exiting..."
    
    def run(self):
        """Run the main application loop"""
        self.running = True
        
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            # Set terminal to raw mode to capture keystrokes
            tty.setraw(sys.stdin.fileno(), termios.TCSANOW)
            
            # Define key codes for input handling
            KEY_SPACE = 32   # Play/Pause
            KEY_Q = 113      # Quit
            KEY_PLUS = 43    # Volume up
            KEY_MINUS = 45   # Volume down
            KEY_LEFT = 60    # '<' key for previous track
            KEY_RIGHT = 62   # '>' key for next track
            KEY_UP = 65      # 'A' key for up navigation
            KEY_DOWN = 66    # 'B' key for down navigation
            KEY_TAB = 9      # Tab key to switch between artists/songs
            KEY_ENTER = 13   # Enter to play selected song
            
            # Track which panel is active (0 = artists, 1 = songs)
            active_panel = 0
            
            # Use Rich Live Display with a moderate refresh rate
            try:
                with Live(self.render(), refresh_per_second=4, screen=True, auto_refresh=False) as live:
                    while self.running:
                        # Check for keypress with timeout
                        rlist, _, _ = select.select([sys.stdin], [], [], 0.25)
                        if rlist:
                            key = ord(sys.stdin.read(1))
                            
                            # Handle global key commands
                            if key == KEY_Q:
                                self.quit()
                            elif key == KEY_SPACE:
                                self.toggle_play_pause()
                            elif key == KEY_PLUS:
                                self.player.set_volume(self.player.volume + 0.1)
                                self.status_message = f"Volume: {int(self.player.volume * 100)}%"
                            elif key == KEY_MINUS:
                                self.player.set_volume(self.player.volume - 0.1)
                                self.status_message = f"Volume: {int(self.player.volume * 100)}%"
                            elif key == KEY_LEFT:
                                self.previous_track()
                            elif key == KEY_RIGHT:
                                self.next_track()
                            elif key == KEY_TAB:
                                # Toggle active panel
                                active_panel = 1 - active_panel
                                self.status_message = f"Active panel: {'Songs' if active_panel == 1 else 'Artists'}"
                            elif key == KEY_ENTER:
                                if active_panel == 1 and self.selected_song:
                                    self.play_selected_song()
                            
                            # Handle panel-specific navigation
                            elif key == KEY_UP:
                                if active_panel == 0:
                                    self.select_prev_artist()
                                else:
                                    self.select_prev_song()
                            elif key == KEY_DOWN:
                                if active_panel == 0:
                                    self.select_next_artist()
                                else:
                                    self.select_next_song()
                        
                        # Update the display
                        try:
                            live.update(self.render())
                        except Exception as e:
                            print(f"\nError updating display: {e}")
            except Exception as e:
                print(f"\nError in Live display: {e}")
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
        print("\nThank you for using t3rm1n4l music player!")
    
    def set_status(self, message):
        """Set the status message"""
        self.status_message = message