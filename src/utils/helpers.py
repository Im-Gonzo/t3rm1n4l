"""
Utility helper functions
"""
import os

def find_music_directory():
    """Find the music directory in the project structure"""
    # Start with the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up to project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    # Check for data/music directory
    music_dir = os.path.join(project_root, "data", "music")
    if os.path.exists(music_dir):
        return music_dir
    
    # If not found, return None and let the caller handle it
    return None

def format_duration(seconds):
    """Format duration in seconds to mm:ss"""
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes}:{seconds:02d}"

def extract_track_info_from_filename(filename):
    """Extract artist and title from filename if possible"""
    # Remove file extension
    name = os.path.splitext(filename)[0]
    
    # Handle common patterns
    # Pattern: "01 - Track Name.mp3"
    if ' - ' in name:
        parts = name.split(' - ', 1)
        # Check if first part is just a track number
        if parts[0].strip().isdigit():
            return {"artist": "Unknown Artist", "title": parts[1].strip()}
        return {"artist": parts[0].strip(), "title": parts[1].strip()}
    
    # Otherwise, just use the filename as title
    return {"artist": "Unknown Artist", "title": name.strip()}
