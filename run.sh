#!/bin/bash

# Run the terminal music player with a fixed terminal size
# This uses the terminal escape codes to set window size and colors

# Set terminal title
echo -e "\033]0;t3rm1n4l Music Player\007"

# Set terminal size
echo "Setting terminal size..."
printf '\e[8;36;120t'  # 36 rows, 120 columns

# Set terminal colors (black background, white text)
printf '\e[40m\e[37m'

# Clear the screen
clear

# Print a welcome message
echo "Starting t3rm1n4l music player..."
echo "Loading music library..."
echo ""
echo "Controls:"
echo "  Space: Play/Pause"
echo "  </> keys: Previous/Next track"
echo "  Tab: Switch between Artists/Songs panel"
echo "  Up/Down keys: Navigate panels"
echo "  Enter: Select song to play"
echo "  +/- keys: Volume up/down"
echo "  q: Quit"
echo ""
echo "Press any key to continue..."
read -n 1

# Run the player
python main.py

# Reset terminal
printf '\e[0m'
clear
