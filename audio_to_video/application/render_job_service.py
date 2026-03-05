from __future__ import annotations

import threading
from subprocess import TimeoutExpired
from collections.abc import Callable

from ..domain.models import ProgressUpdate, RenderConfig
from ..domain.validation import validate_render_config
from ..infrastructure.audio_analyzer import CancelledError, analyze_equalizer_levels
from ..infrastructure.ffmpeg import (
    FfmpegError,
    ensure_ffmpeg_available,
    get_audio_duration_seconds,
    open_video_encode_stream,
)
from ..infrastructure.frame_renderer import FrameRenderer


class RenderJobService:
    def __init__(self, sample_rate: int = 44_100):
        self.sample_rate = sample_rate

    def render_video(
        self,
        config: RenderConfig,
        *,
        cancel_event: threading.Event,
        on_progress: Callable[[ProgressUpdate], None] | None = None,
    ) -> None:
        validate_render_config(config)
        ensure_ffmpeg_available()

        duration = get_audio_duration_seconds(config.audio_path)
        if duration <= 0:
            raise FfmpegError("Não foi possível determinar a duração do áudio.")

        expected_frames = max(1, int(duration * config.fps))

        self._emit(on_progress, "analysis", 0.0, "Analisando áudio...")
        levels = analyze_equalizer_levels(
            audio_path=config.audio_path,
            fps=config.fps,
            bands=config.bands,
            sample_rate=self.sample_rate,
            expected_frames=expected_frames,
            cancel_event=cancel_event,
            on_progress=lambda p: self._emit(
                on_progress,
                "analysis",
                p * 0.45,
                "Analisando áudio...",
            ),
        )

        renderer = FrameRenderer(
            width=config.width,
            height=config.height,
            color_start=config.gradient_start,
            color_end=config.gradient_end,
            avatar_path=config.avatar_path,
        )

        self._emit(on_progress, "encoding", 0.45, "Renderizando e codificando vídeo...")
        encoder = open_video_encode_stream(
            output_path=config.output_path,
            audio_path=config.audio_path,
            width=config.width,
            height=config.height,
            fps=config.fps,
        )

        try:
            for frame_index, band_levels in enumerate(levels):
                if cancel_event.is_set():
                    raise CancelledError("Processamento cancelado pelo usuário.")

                frame = renderer.render_frame(band_levels)
                encoder.stdin.write(frame.tobytes())

                done = (frame_index + 1) / len(levels)
                mapped = 0.45 + (done * 0.55)
                self._emit(on_progress, "encoding", mapped, "Renderizando e codificando vídeo...")

            encoder.stdin.close()
            stderr = encoder.stderr.read().decode("utf-8", errors="ignore") if encoder.stderr else ""
            return_code = encoder.wait()
            if return_code != 0:
                raise FfmpegError(stderr.strip() or "Falha no encode com ffmpeg.")

            self._emit(on_progress, "done", 1.0, "Vídeo gerado com sucesso.")
        except Exception:
            if encoder.stdin and not encoder.stdin.closed:
                encoder.stdin.close()
            encoder.kill()
            try:
                encoder.wait(timeout=5)
            except TimeoutExpired:
                pass
            raise

    @staticmethod
    def _emit(
        callback: Callable[[ProgressUpdate], None] | None,
        stage: str,
        progress: float,
        message: str,
    ) -> None:
        if callback is None:
            return
        callback(ProgressUpdate(stage=stage, progress=max(0.0, min(1.0, progress)), message=message))
