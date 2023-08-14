"""Configuration of texts displayed on the map."""

from dataclasses import dataclass

from .color import Color


@dataclass
class Text:
    """Configuration of texts displayed on the map."""

    text: str
    x: float
    y: float
    color: Color = (0, 0, 0)
    font: str | None = None
    font_size: int | None = None
