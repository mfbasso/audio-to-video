from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenderConfig:
    audio_path: Path
    output_path: Path
    gradient_start: str
    gradient_end: str
    avatar_path: Path | None = None
    width: int = 1280
    height: int = 720
    fps: int = 30
    bands: int = 32


@dataclass(frozen=True)
class ProgressUpdate:
    stage: str
    progress: float
    message: str
