# Music Player API Reference

REST API for controlling audio playback on Raspberry Pi devices.

**Base URL:** `http://<pi-ip>:8080`

**Content-Type:** `application/json`

---

## Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service information |
| GET | `/health` | Health check |
| GET | `/api/status` | Current player state |
| GET | `/api/files` | List audio files |
| POST | `/api/play` | Start/resume playback |
| POST | `/api/stop` | Stop playback |
| POST | `/api/pause` | Toggle pause |
| POST | `/api/next` | Next track |
| POST | `/api/previous` | Previous track |
| POST | `/api/volume` | Set volume |
| POST | `/api/rescan` | Rescan music directory |

---

## Endpoints

### GET `/`

Returns basic service information.

**Response:**
```json
{
  "name": "Kitchen",
  "service": "Raspberry Pi Music Player",
  "version": "1.0.0",
  "api_docs": "/docs"
}
```

---

### GET `/health`

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "pi_name": "Kitchen"
}
```

---

### GET `/api/status`

Returns the current player state including track information and playback position.

**Response:**
```json
{
  "state": "playing",
  "current_track": "song.mp3",
  "current_index": 2,
  "track_count": 15,
  "volume": 80,
  "position_ms": 45000,
  "duration_ms": 180000,
  "pi_name": "Kitchen"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `state` | string | `playing`, `paused`, `stopped`, `loading`, or `error` |
| `current_track` | string\|null | Filename of current track, or null if none |
| `current_index` | integer | Zero-based index in playlist |
| `track_count` | integer | Total number of tracks in playlist |
| `volume` | integer | Volume level (0-100) |
| `position_ms` | integer | Current playback position in milliseconds |
| `duration_ms` | integer | Total track duration in milliseconds |
| `pi_name` | string | Configured name of this Pi |

---

### GET `/api/files`

Lists all audio files in the configured music directory.

**Response:**
```json
{
  "files": [
    {
      "index": 0,
      "filename": "track01.mp3",
      "path": "/home/user/music/track01.mp3"
    },
    {
      "index": 1,
      "filename": "track02.flac",
      "path": "/home/user/music/track02.flac"
    }
  ],
  "total": 2
}
```

**Supported formats:** `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`, `.aac`

---

### POST `/api/play`

Starts or resumes playback.

**Request Body (optional):**
```json
{
  "index": 5
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `index` | integer | No | Track index to play (0-based). If omitted, resumes current track or starts from beginning. |

**Response:**
```json
{
  "success": true,
  "message": "Playback started"
}
```

**Behavior:**
- If paused: resumes playback
- If stopped: starts from current track position in playlist
- If `index` provided: plays that specific track
- If no files: returns `success: false`

---

### POST `/api/stop`

Stops playback completely.

**Request Body:** None

**Response:**
```json
{
  "success": true,
  "message": "Playback stopped"
}
```

---

### POST `/api/pause`

Toggles between playing and paused states.

**Request Body:** None

**Response:**
```json
{
  "success": true,
  "message": "Pause toggled"
}
```

**Behavior:**
- If playing: pauses
- If paused: resumes
- If stopped: returns `success: false`

---

### POST `/api/next`

Skips to the next track in the playlist.

**Request Body:** None

**Response:**
```json
{
  "success": true,
  "message": "Skipped to next track"
}
```

**Behavior:**
- Wraps around to first track after last track
- Returns `success: false` if playlist is empty

---

### POST `/api/previous`

Goes to the previous track in the playlist.

**Request Body:** None

**Response:**
```json
{
  "success": true,
  "message": "Went to previous track"
}
```

**Behavior:**
- Wraps around to last track when at first track
- Returns `success: false` if playlist is empty

---

### POST `/api/volume`

Sets the playback volume.

**Request Body:**
```json
{
  "volume": 75
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `volume` | integer | Yes | Volume level from 0 (mute) to 100 (max) |

**Response:**
```json
{
  "success": true,
  "message": "Volume set to 75"
}
```

---

### POST `/api/rescan`

Rescans the music directory for audio files. Use this after adding or removing files.

**Request Body:** None

**Response:**
```json
{
  "success": true,
  "message": "Found 15 audio files"
}
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 422 | Validation error (invalid request body) |
| 500 | Server error |

Validation errors return details:
```json
{
  "detail": [
    {
      "loc": ["body", "volume"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## CORS

The API allows cross-origin requests from any domain, enabling the web frontend to be opened directly from the filesystem.

---

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI:** `http://<pi-ip>:8080/docs`
- **ReDoc:** `http://<pi-ip>:8080/redoc`

---

## Example Usage

### cURL

```bash
# Check status
curl http://192.168.1.100:8080/api/status

# Start playback
curl -X POST http://192.168.1.100:8080/api/play

# Play specific track
curl -X POST http://192.168.1.100:8080/api/play \
  -H "Content-Type: application/json" \
  -d '{"index": 3}'

# Set volume to 50%
curl -X POST http://192.168.1.100:8080/api/volume \
  -H "Content-Type: application/json" \
  -d '{"volume": 50}'

# Pause
curl -X POST http://192.168.1.100:8080/api/pause

# Next track
curl -X POST http://192.168.1.100:8080/api/next
```

### JavaScript

```javascript
const PI_URL = 'http://192.168.1.100:8080';

// Get status
const status = await fetch(`${PI_URL}/api/status`).then(r => r.json());
console.log(`Playing: ${status.current_track}`);

// Play
await fetch(`${PI_URL}/api/play`, { method: 'POST' });

// Set volume
await fetch(`${PI_URL}/api/volume`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ volume: 75 })
});
```

### Python

```python
import requests

PI_URL = 'http://192.168.1.100:8080'

# Get status
status = requests.get(f'{PI_URL}/api/status').json()
print(f"Playing: {status['current_track']}")

# Play
requests.post(f'{PI_URL}/api/play')

# Set volume
requests.post(f'{PI_URL}/api/volume', json={'volume': 75})
```
