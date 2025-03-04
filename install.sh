#!/bin/bash
# Installation script for t3rm1n4l music player

echo "Installing t3rm1n4l music player..."

# Install Python dependencies
pip install -e .

# Make sure pip installed binaries are in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding ~/.local/bin to PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create symbolic link for easier access (alternative method)
if [ ! -f /usr/local/bin/t3r ]; then
    echo "Creating t3r command link..."
    
    # Check if we have sudo access
    if command -v sudo &> /dev/null; then
        sudo ln -sf "$(pwd)/t3r.sh" /usr/local/bin/t3r
        sudo chmod +x /usr/local/bin/t3r
    else
        echo "Warning: sudo not available. You may need to manually create a symlink."
        echo "Run: sudo ln -sf \"$(pwd)/t3r.sh\" /usr/local/bin/t3r"
    fi
fi

echo "Installation complete! You can now run 't3r' to launch the music player."
echo "If the command doesn't work, restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc)."
