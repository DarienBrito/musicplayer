"""Pydantic models for API requests and responses."""
from typing import Optional
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Player status response."""
    state: str = Field(description="Player state: playing, paused, stopped, loading, error")
    current_track: Optional[str] = Field(description="Currently playing filename")
    current_index: int = Field(description="Index of current track in playlist")
    track_count: int = Field(description="Total number of tracks")
    volume: int = Field(ge=0, le=100, description="Volume level 0-100")
    position_ms: int = Field(ge=0, description="Current position in milliseconds")
    duration_ms: int = Field(ge=0, description="Track duration in milliseconds")
    pi_name: str = Field(description="Name of this Pi")


class FileInfo(BaseModel):
    """Audio file information."""
    index: int = Field(description="Index in playlist")
    filename: str = Field(description="Filename")
    path: str = Field(description="Full path")


class FilesResponse(BaseModel):
    """List of audio files."""
    files: list[FileInfo]
    total: int


class PlayRequest(BaseModel):
    """Request to play a specific track."""
    index: Optional[int] = Field(None, ge=0, description="Track index to play")


class VolumeRequest(BaseModel):
    """Request to set volume."""
    volume: int = Field(ge=0, le=100, description="Volume level 0-100")


class ActionResponse(BaseModel):
    """Generic action response."""
    success: bool
    message: str
