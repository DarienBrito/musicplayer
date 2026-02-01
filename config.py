"""Configuration settings for the music player service."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    pi_name: str = "MusicPlayer"
    music_directory: str = str(Path.home() / "music")
    port: int = 8080
    host: str = "0.0.0.0"

    # Supported audio formats
    audio_extensions: tuple = (".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac")

    class Config:
        env_prefix = "MUSICPLAYER_"
        env_file = os.path.expanduser("~/.env")
        env_file_encoding = "utf-8"


settings = Settings()
