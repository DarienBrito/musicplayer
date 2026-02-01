"""API route definitions."""
from fastapi import APIRouter

from .models import (
    StatusResponse,
    FilesResponse,
    FileInfo,
    PlayRequest,
    VolumeRequest,
    ActionResponse
)
from player import AudioPlayer

router = APIRouter(prefix="/api", tags=["player"])

# Import the singleton player instance
from player.audio_player import player


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current player status."""
    return player.get_status()


@router.get("/files", response_model=FilesResponse)
async def get_files():
    """List all audio files in the music directory."""
    files = player.get_files()
    return FilesResponse(
        files=[FileInfo(**f) for f in files],
        total=len(files)
    )


@router.post("/play", response_model=ActionResponse)
async def play(request: PlayRequest = None):
    """Start or resume playback."""
    index = request.index if request else None
    success = player.play(index)
    return ActionResponse(
        success=success,
        message="Playback started" if success else "Failed to start playback"
    )


@router.post("/stop", response_model=ActionResponse)
async def stop():
    """Stop playback."""
    success = player.stop()
    return ActionResponse(
        success=success,
        message="Playback stopped" if success else "Failed to stop"
    )


@router.post("/pause", response_model=ActionResponse)
async def pause():
    """Toggle pause state."""
    success = player.pause()
    return ActionResponse(
        success=success,
        message="Pause toggled" if success else "Failed to toggle pause"
    )


@router.post("/next", response_model=ActionResponse)
async def next_track():
    """Skip to next track."""
    success = player.next_track()
    return ActionResponse(
        success=success,
        message="Skipped to next track" if success else "Failed to skip"
    )


@router.post("/previous", response_model=ActionResponse)
async def previous_track():
    """Go to previous track."""
    success = player.previous_track()
    return ActionResponse(
        success=success,
        message="Went to previous track" if success else "Failed to go back"
    )


@router.post("/volume", response_model=ActionResponse)
async def set_volume(request: VolumeRequest):
    """Set volume level (0-100)."""
    success = player.set_volume(request.volume)
    return ActionResponse(
        success=success,
        message=f"Volume set to {request.volume}" if success else "Failed to set volume"
    )


@router.post("/rescan", response_model=ActionResponse)
async def rescan():
    """Rescan music directory for files."""
    files = player.scan_directory()
    return ActionResponse(
        success=True,
        message=f"Found {len(files)} audio files"
    )
