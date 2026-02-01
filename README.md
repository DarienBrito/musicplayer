# Raspberry Pi Music Player System

A distributed music player system where multiple Raspberry Pis play audio files from local directories, controlled via a web interface.

## Documentation

- **[Setup Guide](docs/SETUP.md)** - Complete Raspberry Pi installation instructions
- **[API Reference](docs/API.md)** - Full API documentation with examples

## Quick Start

### On each Raspberry Pi

```bash
# Install dependencies
sudo apt update && sudo apt install -y vlc python3-venv git

# Clone or copy the project
git clone <repo> ~/musicplayer
cd ~/musicplayer/pi-service

# Run the installer
chmod +x install.sh
./install.sh

# Configure your Pi
nano ~/.env
# Set: MUSICPLAYER_PI_NAME=Kitchen
# Set: MUSICPLAYER_MUSIC_DIRECTORY=/home/pi/music

# Add music files
cp /path/to/your/music/*.mp3 ~/music/

# Start the service
sudo systemctl start musicplayer

# Verify it's running
curl http://localhost:8080/api/status
```

### Web Interface

Open `web-frontend/index.html` directly in any browser - no server required.

1. Click "Add Pi"
2. Enter the Pi's IP address (e.g., `192.168.1.100`)
3. Control playback with the on-screen buttons

## Project Structure

```
RaspberryPi/
├── pi-service/              # Runs on each Raspberry Pi
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings from environment
│   ├── requirements.txt     # Python dependencies
│   ├── player/
│   │   └── audio_player.py  # VLC wrapper
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── models.py        # Request/response schemas
│   ├── musicplayer.service  # systemd unit file
│   └── install.sh           # Installation script
│
├── web-frontend/            # Open locally in browser
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── app.js           # Main UI logic
│       ├── api.js           # Pi API client
│       └── storage.js       # localStorage for Pi list
│
└── docs/
    ├── API.md               # API reference
    └── SETUP.md             # Pi setup guide
```

## API Overview

Each Pi exposes a REST API on port 8080:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Player state, track, volume |
| GET | `/api/files` | List audio files |
| POST | `/api/play` | Start playback |
| POST | `/api/stop` | Stop playback |
| POST | `/api/pause` | Toggle pause |
| POST | `/api/next` | Next track |
| POST | `/api/previous` | Previous track |
| POST | `/api/volume` | Set volume (0-100) |

See [API Reference](docs/API.md) for complete documentation.

## Configuration

Edit `~/.env` on each Pi:

```bash
MUSICPLAYER_PI_NAME=Kitchen                    # Display name
MUSICPLAYER_MUSIC_DIRECTORY=/home/pi/music     # Path to audio files
MUSICPLAYER_PORT=8080                          # API port
```

## Supported Audio Formats

MP3, WAV, FLAC, OGG, M4A, AAC

## Service Management

```bash
sudo systemctl start musicplayer      # Start
sudo systemctl stop musicplayer       # Stop
sudo systemctl restart musicplayer    # Restart
journalctl -u musicplayer -f          # View logs
```

## Troubleshooting

See the [Setup Guide](docs/SETUP.md#troubleshooting) for common issues and solutions.
