from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


class FrameRenderer:
    def __init__(self, width: int, height: int, color_start: str, color_end: str, avatar_path: Path | None):
        self.width = width
        self.height = height
        self.color_start = _hex_to_rgb(color_start)
        self.color_end = _hex_to_rgb(color_end)
        self.background = self._build_gradient_background()
        self.avatar = _load_avatar(avatar_path, width=width, height=height)

    def render_frame(self, band_levels: np.ndarray) -> Image.Image:
        frame = self.background.copy()
        draw = ImageDraw.Draw(frame)

        bands = len(band_levels)
        chart_width = int(self.width * 0.82)
        left = (self.width - chart_width) // 2
        right = left + chart_width
        max_half_height = int(self.height * 0.225)
        center_y = self.height // 2
        spacing = 4
        total_spacing = spacing * (bands - 1)
        bar_width = max(2, (chart_width - total_spacing) // bands)

        for idx, level in enumerate(band_levels):
            level_height = int(max_half_height * float(np.clip(level, 0.0, 1.0)))
            x0 = left + idx * (bar_width + spacing)
            x1 = min(x0 + bar_width, right)
            y0 = center_y - level_height
            y1 = center_y + level_height

            draw.rectangle([x0, y0, x1, y1], fill=(246, 246, 246, 255))

        if self.avatar:
            avatar_x = (self.width - self.avatar.width) // 2
            avatar_y = int(self.height * 0.08)
            frame.alpha_composite(self.avatar, (avatar_x, avatar_y))

        return frame.convert("RGB")

    def _build_gradient_background(self) -> Image.Image:
        image = Image.new("RGBA", (self.width, self.height))
        draw = ImageDraw.Draw(image)
        for y in range(self.height):
            ratio = y / max(1, self.height - 1)
            color = (
                int(self.color_start[0] * (1 - ratio) + self.color_end[0] * ratio),
                int(self.color_start[1] * (1 - ratio) + self.color_end[1] * ratio),
                int(self.color_start[2] * (1 - ratio) + self.color_end[2] * ratio),
                255,
            )
            draw.line([(0, y), (self.width, y)], fill=color)
        return image


def _load_avatar(avatar_path: Path | None, *, width: int, height: int) -> Image.Image | None:
    if avatar_path is None:
        return None

    avatar = Image.open(avatar_path).convert("RGBA")
    target_size = int(min(width, height) * 0.22)
    avatar.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

    mask = Image.new("L", avatar.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)
    avatar.putalpha(mask)
    return avatar


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
