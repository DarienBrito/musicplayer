# Raspberry Pi Setup Guide

Complete instructions for setting up the Music Player service on a Raspberry Pi.

---

## Prerequisites

- Raspberry Pi (any model with audio output)
- Raspberry Pi OS (Bullseye or newer recommended)
- Network connection (Ethernet or WiFi)
- Audio output configured (3.5mm jack, HDMI, or USB audio)
- SSH access or direct keyboard/monitor

---

## Step 1: Initial Pi Setup

If starting with a fresh Raspberry Pi OS installation:

```bash
# Update the system
sudo apt update && sudo apt upgrade -y

# Configure audio output
sudo raspi-config
# Navigate to: System Options > Audio > Choose your output
```

---

## Step 2: Install System Dependencies

```bash
# Install VLC and Python
sudo apt install -y vlc python3-venv python3-pip git

# Verify VLC installation
cvlc --version
```

**Note:** On headless Pi (no desktop), VLC runs in console mode which is fine for audio playback.

---

## Step 3: Download the Music Player

### Option A: Clone from Git repository

```bash
cd ~
git clone https://github.com/DarienBrito/musicplayer musicplayer
```

### Option B: Copy files manually

Copy the `musicplayer` folder to your home directory using SCP, USB drive, or other method:

```bash
# From your computer (replace <username> with your Pi username):
scp -r musicplayer/ <username>@<pi-ip>:~/
```

---

## Step 4: Run the Installer

```bash
cd ~/musicplayer/
chmod +x install.sh
./install.sh
```

The installer will:
1. Install VLC and Python dependencies
2. Create a Python virtual environment
3. Install the required Python packages
4. Create a default music directory (`~/music`)
5. Create a default configuration file (`~/.env`)
6. Install and enable the systemd service

---

## Step 5: Configure Your Pi

Edit the configuration file:

```bash
nano ~/.env
```

Set your preferences:

```bash
# Display name shown in the web interface
MUSICPLAYER_PI_NAME=Kitchen

# Path to your music files
# IMPORTANT: Replace with your actual home directory path
# Run 'echo $HOME' to find your home directory
MUSICPLAYER_MUSIC_DIRECTORY=/home/pi/music

# API port (default 8080)
MUSICPLAYER_PORT=8080
```

**Important:** Make sure `MUSICPLAYER_MUSIC_DIRECTORY` points to your actual music folder. The install script sets this automatically, but verify the path matches where your audio files are stored.

Save and exit (Ctrl+X, Y, Enter).

---

## Step 6: Add Music Files

Copy audio files to your music directory:

```bash
# Create directory if it doesn't exist
mkdir -p ~/music

# Copy files (examples)
cp /media/usb/*.mp3 ~/music/

# or copy from main computer
scp -r "D:/Music/*" pi@pi:~/music/
```

**Supported formats:** MP3, WAV, FLAC, OGG, M4A, AAC

---

## Step 7: Start the Service

```bash
# Set hostname (optional, helps identify the Pi)
sudo hostnamectl set-hostname kitchen-pi

# Start the service
sudo systemctl start musicplayer

# Check it's running
sudo systemctl status musicplayer

# View logs
journalctl -u musicplayer -f
```

---

## Step 8: Test the API

```bash
# Test from the Pi itself
curl http://localhost:8080/api/status

# Test from another computer (replace with your Pi's IP)
curl http://192.168.1.100:8080/api/status
```

Expected response:
```json
{
  "state": "stopped",
  "current_track": null,
  "current_index": 0,
  "track_count": 5,
  "volume": 80,
  "position_ms": 0,
  "duration_ms": 0,
  "pi_name": "Kitchen"
}
```

---

## Step 9: Connect from Web Interface

1. Open `web-frontend/index.html` in any browser
2. Click "Add Pi"
3. Enter your Pi's IP address and port
4. Control playback!

To find your Pi's IP address:
```bash
hostname -I
```

---

## Service Management

### Start/Stop/Restart

```bash
sudo systemctl start musicplayer
sudo systemctl stop musicplayer
sudo systemctl restart musicplayer
```

### Enable/Disable Auto-start

```bash
# Start on boot (enabled by default)
sudo systemctl enable musicplayer

# Don't start on boot
sudo systemctl disable musicplayer
```

### View Logs

```bash
# Follow logs in real-time
journalctl -u musicplayer -f

# View last 50 lines
journalctl -u musicplayer -n 50

# View logs since boot
journalctl -u musicplayer -b
```

---

## Audio Configuration

### Check Audio Devices

```bash
# List audio devices
aplay -l

# Test audio output
speaker-test -t wav -c 2
```

### Set Default Output

```bash
sudo raspi-config
# System Options > Audio > Select output
```

Or edit ALSA config manually:

```bash
# For 3.5mm jack (analog)
amixer cset numid=3 1

# For HDMI
amixer cset numid=3 2

# For auto-detect
amixer cset numid=3 0
```

### USB Audio Device

If using a USB sound card:

```bash
# Find the card number
aplay -l

# Set as default in ~/.asoundrc
cat > ~/.asoundrc << 'EOF'
defaults.pcm.card 1
defaults.ctl.card 1
EOF
```

### VLC Audio Output

By default, VLC is configured to use the 3.5mm headphone jack. If you need to change the audio output, edit `~/musicplayer/player/audio_player.py`:

```python
# Line 17 - change the audio device:
self._instance = vlc.Instance(
    "--no-xlib",
    "--aout=alsa",
    "--alsa-audio-device=plughw:1,0"  # Change this line
)
```

Common device options:
- **Headphone jack (3.5mm):** `plughw:1,0`
- **HDMI:** `plughw:0,0`
- **USB audio:** `plughw:2,0` (check `aplay -l` for card number)

After changing, restart the service:
```bash
sudo systemctl restart musicplayer
```

---

## Network Configuration

### Static IP (Recommended)

Edit dhcpcd configuration:

```bash
sudo nano /etc/dhcpcd.conf
```

Add at the bottom:

```
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

For WiFi, use `interface wlan0` instead.

### Firewall

If using UFW firewall:

```bash
sudo ufw allow 8080/tcp
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
journalctl -u musicplayer -n 50

# Run manually to see output
cd ~/musicplayer
source ~/musicplayer/venv/bin/activate
python main.py
```

### No Audio Files Found

If the API returns `"track_count": 0`, check that `MUSICPLAYER_MUSIC_DIRECTORY` in `~/.env` points to the correct path:

```bash
# Check current config
cat ~/.env

# Verify music directory exists and has files
ls ~/music/

# Fix the path if needed (replace /home/pi with your actual home)
nano ~/.env

# Restart service after changes
sudo systemctl restart musicplayer

# Verify files are found
curl http://localhost:8080/api/files
```

**Note:** The installer skips creating `~/.env` if it already exists. If you reinstalled, your old config may have an incorrect path.

### No Audio Output

If the player shows "playing" but no sound is heard:

```bash
# List available audio devices
aplay -l

# Test the headphone jack directly
speaker-test -D plughw:1,0 -c 2 -t sine -f 440 -l 1

# Test VLC with explicit output device
cvlc --aout=alsa --alsa-audio-device=plughw:1,0 --play-and-exit ~/music/test.mp3

# Check volume
amixer -c 1 get PCM
```

**Common cause:** VLC defaults to HDMI output instead of the headphone jack. The music player is configured for headphones (`plughw:1,0`). If you're using HDMI, edit `~/musicplayer/player/audio_player.py` and change `plughw:1,0` to `plughw:0,0`. See [VLC Audio Output](#vlc-audio-output) for details.

### Can't Connect from Browser

```bash
# Verify service is running
curl http://localhost:8080/health

# Check if port is open
ss -tlnp | grep 8080

# Check firewall
sudo iptables -L -n | grep 8080

# Verify network connectivity
ping <pi-ip>
```

### VLC Errors

```bash
# Reinstall VLC
sudo apt install --reinstall vlc

# Check for missing codecs
sudo apt install vlc-plugin-base
```

### Permission Denied

```bash
# Fix ownership (use your actual username)
sudo chown -R $(whoami):$(whoami) ~/musicplayer
sudo chown $(whoami):$(whoami) ~/.env

# Fix audio group membership
sudo usermod -aG audio $(whoami)
# Then reboot
```

---

## Updating

To update to a new version:

```bash
cd ~/musicplayer

# If using git
git pull

# Restart service
sudo systemctl restart musicplayer
```

---

## Uninstalling

```bash
# Stop and disable service
sudo systemctl stop musicplayer
sudo systemctl disable musicplayer

# Remove service file
sudo rm /etc/systemd/system/musicplayer.service
sudo systemctl daemon-reload

# Remove files (optional)
rm -rf ~/musicplayer
rm ~/.env
```

---

## Multiple Pis Setup

To set up multiple Pis:

1. Follow these instructions on each Pi
2. Give each Pi a unique name in `~/.env`
3. Optionally assign static IPs to each
4. Add all Pis to the web interface

Example naming scheme:
- Kitchen Pi: `MUSICPLAYER_PI_NAME=Kitchen`
- Bedroom Pi: `MUSICPLAYER_PI_NAME=Bedroom`
- Living Room Pi: `MUSICPLAYER_PI_NAME=Living Room`

---

## Security Notes

- The API has no authentication - only use on trusted local networks
- CORS is open to allow browser access from any origin
- Consider using a VPN if remote access is needed
- Don't expose port 8080 to the internet

---

## SSH Key Authentication (Recommended)

Disable password authentication for improved security by using SSH keys.

### 1. Generate SSH Key (on your computer)

Skip if you already have a key at `~/.ssh/id_ed25519.pub`.

**Linux/Mac:**
```bash
ssh-keygen -t ed25519
```

**Windows PowerShell:**
```powershell
ssh-keygen -t ed25519
```

### 2. Copy Key to Pi

**Linux/Mac:**
```bash
ssh-copy-id pi@<pi-ip>
```

**Windows PowerShell:**
```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh pi@<pi-ip> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

**Manual method (any OS):**
```bash
# Display your public key
cat ~/.ssh/id_ed25519.pub

# SSH into the Pi
ssh pi@<pi-ip>

# On the Pi, add the key
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
# Paste your public key, save (Ctrl+X, Y, Enter)

# Set permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 3. Test Key Login

Open a **new terminal** and verify you can connect without a password:
```bash
ssh pi@<pi-ip>
```

### 4. Disable Password Authentication

**Important:** Keep your current SSH session open until you verify key login works.

On the Pi, edit SSH config:
```bash
sudo nano /etc/ssh/sshd_config
```

Find and change (or add) these lines:
```
PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no
```

Restart SSH:
```bash
sudo systemctl restart ssh
```

### Recovery

If locked out, you'll need physical access to the Pi:
- Connect keyboard and monitor, or
- Mount the SD card on another computer and edit `/etc/ssh/sshd_config`

---

## Quick Reference

| Task | Command |
|------|---------|
| Start service | `sudo systemctl start musicplayer` |
| Stop service | `sudo systemctl stop musicplayer` |
| View logs | `journalctl -u musicplayer -f` |
| Check status | `curl http://localhost:8080/api/status` |
| Edit config | `nano ~/.env` |
| Add music | `cp *.mp3 ~/music/` |
| Find IP | `hostname -I` |
