from __future__ import annotations

from pathlib import Path

from .models import RenderConfig


class ValidationError(ValueError):
    pass


SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def validate_render_config(config: RenderConfig) -> None:
    if not config.audio_path.exists() or not config.audio_path.is_file():
        raise ValidationError("O arquivo de áudio não existe.")

    if config.audio_path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValidationError("Formato de áudio não suportado.")

    if config.avatar_path:
        if not config.avatar_path.exists() or not config.avatar_path.is_file():
            raise ValidationError("A imagem de avatar não existe.")
        if config.avatar_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            raise ValidationError("Formato de avatar não suportado.")

    if config.width <= 0 or config.height <= 0:
        raise ValidationError("Resolução inválida.")

    if config.fps <= 0:
        raise ValidationError("FPS inválido.")

    if config.bands <= 0:
        raise ValidationError("Quantidade de bandas inválida.")

    if not _is_hex_color(config.gradient_start) or not _is_hex_color(config.gradient_end):
        raise ValidationError("As cores do gradiente devem estar no formato hexadecimal #RRGGBB.")

    output_parent = config.output_path.parent
    if not output_parent.exists():
        raise ValidationError("A pasta de destino não existe.")

    if config.output_path.suffix.lower() != ".mp4":
        raise ValidationError("A saída do MVP deve ser .mp4.")


def _is_hex_color(color: str) -> bool:
    if not isinstance(color, str) or len(color) != 7 or not color.startswith("#"):
        return False

    value = color[1:]
    return all(char in "0123456789abcdefABCDEF" for char in value)
