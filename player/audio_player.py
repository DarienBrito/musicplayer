"""VLC-based audio player with playlist support."""
import os
from pathlib import Path
from typing import Optional
import vlc

from config import settings


class AudioPlayer:
    """Manages audio playback using VLC."""

    def __init__(self):
        self._instance = vlc.Instance("--no-xlib")
        self._player: vlc.MediaPlayer = self._instance.media_player_new()
        self._playlist: list[str] = []
        self._current_index: int = 0
        self._volume: int = 80

        # Set initial volume
        self._player.audio_set_volume(self._volume)

        # Set up end-of-track callback
        events = self._player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_track_end)

        # Scan for files on initialization
        self.scan_directory()

    def _on_track_end(self, event):
        """Handle track ending - play next track."""
        # Schedule next track (can't call directly from callback)
        import threading
        threading.Thread(target=self._play_next_auto, daemon=True).start()

    def _play_next_auto(self):
        """Auto-advance to next track when current ends."""
        import time
        time.sleep(0.1)  # Small delay to let VLC clean up
        if self._playlist:
            self._current_index = (self._current_index + 1) % len(self._playlist)
            self._load_and_play(self._playlist[self._current_index])

    def scan_directory(self) -> list[str]:
        """Scan music directory for audio files."""
        music_dir = Path(settings.music_directory)
        self._playlist = []

        if not music_dir.exists():
            return self._playlist

        for file_path in sorted(music_dir.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in settings.audio_extensions:
                self._playlist.append(str(file_path))

        return self._playlist

    def get_files(self) -> list[dict]:
        """Get list of audio files with metadata."""
        files = []
        for i, file_path in enumerate(self._playlist):
            path = Path(file_path)
            files.append({
                "index": i,
                "filename": path.name,
                "path": str(path)
            })
        return files

    def _load_and_play(self, file_path: str):
        """Load a file and start playback."""
        media = self._instance.media_new(file_path)
        self._player.set_media(media)
        self._player.play()
        self._player.audio_set_volume(self._volume)

    def play(self, index: Optional[int] = None) -> bool:
        """Start or resume playback."""
        if not self._playlist:
            return False

        state = self._player.get_state()

        # If index specified, play that track
        if index is not None:
            if 0 <= index < len(self._playlist):
                self._current_index = index
                self._load_and_play(self._playlist[self._current_index])
                return True
            return False

        # If paused, resume
        if state == vlc.State.Paused:
            self._player.play()
            return True

        # If stopped or ended, start from current index
        if state in (vlc.State.Stopped, vlc.State.Ended, vlc.State.NothingSpecial):
            self._load_and_play(self._playlist[self._current_index])
            return True

        # Already playing
        return True

    def stop(self) -> bool:
        """Stop playback."""
        self._player.stop()
        return True

    def pause(self) -> bool:
        """Toggle pause state."""
        state = self._player.get_state()
        if state == vlc.State.Playing:
            self._player.pause()
            return True
        elif state == vlc.State.Paused:
            self._player.play()
            return True
        return False

    def next_track(self) -> bool:
        """Skip to next track."""
        if not self._playlist:
            return False
        self._current_index = (self._current_index + 1) % len(self._playlist)
        self._load_and_play(self._playlist[self._current_index])
        return True

    def previous_track(self) -> bool:
        """Go to previous track."""
        if not self._playlist:
            return False
        self._current_index = (self._current_index - 1) % len(self._playlist)
        self._load_and_play(self._playlist[self._current_index])
        return True

    def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)."""
        self._volume = max(0, min(100, volume))
        self._player.audio_set_volume(self._volume)
        return True

    def get_status(self) -> dict:
        """Get current player status."""
        state = self._player.get_state()

        # Map VLC states to simple strings
        state_map = {
            vlc.State.NothingSpecial: "stopped",
            vlc.State.Opening: "loading",
            vlc.State.Buffering: "loading",
            vlc.State.Playing: "playing",
            vlc.State.Paused: "paused",
            vlc.State.Stopped: "stopped",
            vlc.State.Ended: "stopped",
            vlc.State.Error: "error"
        }

        current_file = None
        if self._playlist and 0 <= self._current_index < len(self._playlist):
            current_file = Path(self._playlist[self._current_index]).name

        # Get position/duration
        position = self._player.get_time()
        duration = self._player.get_length()

        return {
            "state": state_map.get(state, "unknown"),
            "current_track": current_file,
            "current_index": self._current_index,
            "track_count": len(self._playlist),
            "volume": self._volume,
            "position_ms": max(0, position),
            "duration_ms": max(0, duration),
            "pi_name": settings.pi_name
        }


# Singleton instance
player = AudioPlayer()
