# t3rm1n4l Music Player

A feature-rich terminal-based music player written in Python.

## Features

- Play, pause, stop music directly in your terminal
- Browse and manage your music library
- Create and manage playlists
- Search for tracks by title, artist, or album
- Beautiful terminal UI with colors and controls
- Keyboard shortcuts for easy navigation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/t3rm1n4l.git
cd t3rm1n4l
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the player:
```bash
python main.py
```

### Keyboard Controls

- **Space**: Play/Pause
- **<**: Previous track
- **>**: Next track
- **+**: Increase volume
- **-**: Decrease volume
- **s**: Search
- **p**: Playlist menu
- **q**: Quit

## Project Structure

```
t3rm1n4l/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── README.md            # Documentation
├── src/                 # Source code
│   ├── ui/              # User interface components
│   ├── player/          # Audio playback functionality
│   ├── library/         # Library management
│   └── utils/           # Utility functions
├── tests/               # Unit tests
└── data/                # Library data and playlists
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
