from __future__ import annotations

import math
import threading
from collections.abc import Callable

import numpy as np

from .ffmpeg import FfmpegError, open_audio_pcm_stream


class CancelledError(RuntimeError):
    pass


def analyze_equalizer_levels(
    *,
    audio_path,
    fps: int,
    bands: int,
    sample_rate: int,
    expected_frames: int,
    cancel_event: threading.Event,
    on_progress: Callable[[float], None] | None = None,
) -> list[np.ndarray]:
    process = open_audio_pcm_stream(audio_path, sample_rate=sample_rate)
    samples_per_frame = max(1, sample_rate // fps)
    bytes_per_frame = samples_per_frame * 4
    window = np.hanning(samples_per_frame).astype(np.float32)
    frequency_bins = np.fft.rfftfreq(samples_per_frame, d=1.0 / sample_rate)
    bands_limits = _log_band_limits(frequency_bins, bands)

    levels: list[np.ndarray] = []
    running_peak = 1e-6
    cancelled = False

    try:
        for frame_index in range(expected_frames):
            if cancel_event.is_set():
                cancelled = True
                process.terminate()
                raise CancelledError("Processamento cancelado pelo usuário.")

            chunk = process.stdout.read(bytes_per_frame)
            if not chunk:
                frame_samples = np.zeros(samples_per_frame, dtype=np.float32)
            else:
                frame_samples = np.frombuffer(chunk, dtype=np.float32)
                if frame_samples.size < samples_per_frame:
                    frame_samples = np.pad(
                        frame_samples,
                        (0, samples_per_frame - frame_samples.size),
                        mode="constant",
                    )

            spectrum = np.abs(np.fft.rfft(frame_samples * window))
            band_values = np.zeros(bands, dtype=np.float32)
            for band_index, (start_idx, end_idx) in enumerate(bands_limits):
                if end_idx <= start_idx:
                    value = float(spectrum[start_idx])
                else:
                    value = float(np.mean(spectrum[start_idx:end_idx]))
                band_values[band_index] = value

            running_peak = max(running_peak, float(np.max(band_values)))
            normalized = np.clip(band_values / running_peak, 0.0, 1.0)
            compressed = np.sqrt(normalized)
            levels.append(compressed)

            if on_progress:
                on_progress((frame_index + 1) / expected_frames)
    finally:
        process.stdout.close()
        stderr = process.stderr.read().decode("utf-8", errors="ignore") if process.stderr else ""
        return_code = process.wait()
        if return_code != 0 and not cancelled:
            raise FfmpegError(stderr.strip() or "Falha ao analisar áudio com ffmpeg.")

    return _smooth_levels(levels)


def _log_band_limits(frequency_bins: np.ndarray, bands: int) -> list[tuple[int, int]]:
    min_freq = 20.0
    max_freq = min(16000.0, float(frequency_bins[-1]))
    if max_freq <= min_freq:
        max_freq = min_freq * 2
    freq_limits = np.logspace(math.log10(min_freq), math.log10(max_freq), num=bands + 1)

    limits: list[tuple[int, int]] = []
    for index in range(bands):
        start_freq = freq_limits[index]
        end_freq = freq_limits[index + 1]
        start_idx = int(np.searchsorted(frequency_bins, start_freq, side="left"))
        end_idx = int(np.searchsorted(frequency_bins, end_freq, side="right"))
        start_idx = min(start_idx, len(frequency_bins) - 1)
        end_idx = min(max(end_idx, start_idx + 1), len(frequency_bins))
        limits.append((start_idx, end_idx))
    return limits


def _smooth_levels(levels: list[np.ndarray], alpha: float = 0.45) -> list[np.ndarray]:
    if not levels:
        return levels

    smoothed: list[np.ndarray] = []
    prev = levels[0]
    smoothed.append(prev)
    for current in levels[1:]:
        mixed = (alpha * current) + ((1 - alpha) * prev)
        smoothed.append(mixed)
        prev = mixed
    return smoothed
