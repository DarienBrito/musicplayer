"""Configuration settings for the music player service."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from ~/.env
load_dotenv(Path.home() / ".env")


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.pi_name = os.getenv("MUSICPLAYER_PI_NAME", "MusicPlayer")
        self.music_directory = os.getenv("MUSICPLAYER_MUSIC_DIRECTORY", str(Path.home() / "music"))
        self.port = int(os.getenv("MUSICPLAYER_PORT", "8080"))
        self.host = os.getenv("MUSICPLAYER_HOST", "0.0.0.0")
        self.audio_extensions = (".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac")


settings = Settings()
