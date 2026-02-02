"""API route definitions."""
from typing import Optional
from fastapi import APIRouter, Body

router = APIRouter(prefix="/api", tags=["player"])

# Import the singleton player instance
from player.audio_player import player


@router.get("/status")
async def get_status():
    """Get current player status."""
    return player.get_status()


@router.get("/files")
async def get_files():
    """List all audio files in the music directory."""
    files = player.get_files()
    return {"files": files, "total": len(files)}


@router.post("/play")
async def play(index: Optional[int] = Body(None, embed=True)):
    """Start or resume playback."""
    success = player.play(index)
    return {
        "success": success,
        "message": "Playback started" if success else "Failed to start playback"
    }


@router.post("/stop")
async def stop():
    """Stop playback."""
    success = player.stop()
    return {
        "success": success,
        "message": "Playback stopped" if success else "Failed to stop"
    }


@router.post("/pause")
async def pause():
    """Toggle pause state."""
    success = player.pause()
    return {
        "success": success,
        "message": "Pause toggled" if success else "Failed to toggle pause"
    }


@router.post("/next")
async def next_track():
    """Skip to next track."""
    success = player.next_track()
    return {
        "success": success,
        "message": "Skipped to next track" if success else "Failed to skip"
    }


@router.post("/previous")
async def previous_track():
    """Go to previous track."""
    success = player.previous_track()
    return {
        "success": success,
        "message": "Went to previous track" if success else "Failed to go back"
    }


@router.post("/volume")
async def set_volume(volume: int = Body(..., embed=True, ge=0, le=100)):
    """Set volume level (0-100)."""
    success = player.set_volume(volume)
    return {
        "success": success,
        "message": f"Volume set to {volume}" if success else "Failed to set volume"
    }


@router.post("/rescan")
async def rescan():
    """Rescan music directory for files."""
    files = player.scan_directory()
    return {
        "success": True,
        "message": f"Found {len(files)} audio files"
    }


@router.post("/shuffle")
async def shuffle():
    """Shuffle the playlist order."""
    success = player.shuffle()
    return {
        "success": success,
        "message": "Playlist shuffled" if success else "Failed to shuffle (no files)"
    }
