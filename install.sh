#!/bin/bash
# Installation script for Raspberry Pi Music Player

set -e

echo "=== Raspberry Pi Music Player Installation ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Get current user info
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)

# Check if running as root
if [ "$CURRENT_USER" = "root" ]; then
    echo -e "${RED}Error: Do not run this script as root.${NC}"
    echo "Run as your normal user: ./install.sh"
    exit 1
fi

# Check if running on Pi
if [ ! -f /etc/rpi-issue ] && [ ! -d /boot/firmware ]; then
    echo -e "${RED}Warning: This doesn't appear to be a Raspberry Pi.${NC}"
    echo "Continuing anyway..."
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_DIR="$USER_HOME/musicplayer"
VENV_DIR="$INSTALL_DIR/venv"

echo ""
echo "Installing for user: $CURRENT_USER"
echo "Install directory: $INSTALL_DIR"
echo ""

echo "1. Installing system dependencies..."
sudo apt update
sudo apt install -y vlc python3-venv python3-pip

echo ""
echo "2. Setting up installation directory..."
if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
fi

echo ""
echo "3. Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo ""
echo "4. Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$INSTALL_DIR/requirements.txt"

echo ""
echo "5. Creating default music directory..."
mkdir -p "$USER_HOME/music"

echo ""
echo "6. Creating default configuration..."
if [ ! -f "$USER_HOME/.env" ]; then
    cat > "$USER_HOME/.env" << EOF
MUSICPLAYER_PI_NAME=MusicPlayer
MUSICPLAYER_MUSIC_DIRECTORY=$USER_HOME/music
MUSICPLAYER_PORT=8080
EOF
    echo "Created $USER_HOME/.env - edit this to customize your Pi name and music directory"
else
    echo "$USER_HOME/.env already exists, skipping..."
fi

echo ""
echo "7. Generating systemd service file..."
cat > "$INSTALL_DIR/musicplayer.service" << EOF
[Unit]
Description=Raspberry Pi Music Player Service
After=network.target sound.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$VENV_DIR/bin:/usr/bin:/bin
EnvironmentFile=$USER_HOME/.env
ExecStart=$VENV_DIR/bin/python main.py
Restart=always
RestartSec=5

# Give VLC time to initialize audio
ExecStartPre=/bin/sleep 2

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "8. Installing systemd service..."
sudo cp "$INSTALL_DIR/musicplayer.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable musicplayer.service

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit your configuration: nano ~/.env"
echo "  2. Add music files to: $USER_HOME/music/"
echo "  3. Start the service: sudo systemctl start musicplayer"
echo "  4. Check status: sudo systemctl status musicplayer"
echo ""
echo "The service will start automatically on boot."
echo "Access the API at: http://$(hostname -I | awk '{print $1}'):8080"
echo ""
