from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class FfmpegError(RuntimeError):
    pass


def ensure_ffmpeg_available() -> None:
    if shutil.which("ffmpeg") is None:
        raise FfmpegError("ffmpeg não encontrado no sistema.")
    if shutil.which("ffprobe") is None:
        raise FfmpegError("ffprobe não encontrado no sistema.")


def get_audio_duration_seconds(audio_path: Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(audio_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise FfmpegError(result.stderr.strip() or "Falha ao obter duração do áudio.")

    try:
        payload = json.loads(result.stdout)
        duration = float(payload["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise FfmpegError("Não foi possível interpretar a duração do áudio.") from exc

    return max(0.0, duration)


def open_audio_pcm_stream(audio_path: Path, sample_rate: int) -> subprocess.Popen[bytes]:
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-i",
        str(audio_path),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-f",
        "f32le",
        "pipe:1",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.stdout is None:
        raise FfmpegError("Não foi possível abrir o stream PCM do áudio.")
    return process


def open_video_encode_stream(
    *,
    output_path: Path,
    audio_path: Path,
    width: int,
    height: int,
    fps: int,
) -> subprocess.Popen[bytes]:
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "pipe:0",
        "-i",
        str(audio_path),
        "-shortest",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        str(output_path),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.stdin is None:
        raise FfmpegError("Não foi possível abrir o stream de encode de vídeo.")
    return process
