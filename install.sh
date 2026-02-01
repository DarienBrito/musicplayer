#!/bin/bash
# Installation script for Raspberry Pi Music Player

set -e

echo "=== Raspberry Pi Music Player Installation ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if running on Pi
if [ ! -f /etc/rpi-issue ] && [ ! -d /boot/firmware ]; then
    echo -e "${RED}Warning: This doesn't appear to be a Raspberry Pi.${NC}"
    echo "Continuing anyway..."
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INSTALL_DIR="/home/pi/musicplayer"
VENV_DIR="$INSTALL_DIR/venv"

echo ""
echo "1. Installing system dependencies..."
sudo apt update
sudo apt install -y vlc python3-venv python3-pip

echo ""
echo "2. Creating installation directory..."
if [ "$SCRIPT_DIR" != "$INSTALL_DIR/pi-service" ]; then
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown pi:pi "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR" "$INSTALL_DIR/pi-service"
fi

echo ""
echo "3. Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo ""
echo "4. Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$INSTALL_DIR/pi-service/requirements.txt"

echo ""
echo "5. Creating default music directory..."
mkdir -p /home/pi/music

echo ""
echo "6. Creating default configuration..."
if [ ! -f /home/pi/.env ]; then
    cat > /home/pi/.env << EOF
MUSICPLAYER_PI_NAME=MusicPlayer
MUSICPLAYER_MUSIC_DIRECTORY=/home/pi/music
MUSICPLAYER_PORT=8080
EOF
    echo "Created /home/pi/.env - edit this to customize your Pi name and music directory"
else
    echo "/home/pi/.env already exists, skipping..."
fi

echo ""
echo "7. Installing systemd service..."
sudo cp "$INSTALL_DIR/pi-service/musicplayer.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable musicplayer.service

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit your configuration: nano ~/.env"
echo "  2. Add music files to: /home/pi/music/"
echo "  3. Start the service: sudo systemctl start musicplayer"
echo "  4. Check status: sudo systemctl status musicplayer"
echo ""
echo "The service will start automatically on boot."
echo "Access the API at: http://$(hostname -I | awk '{print $1}'):8080"
echo ""
