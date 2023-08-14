"""Configuration of map dimensions."""

from dataclasses import dataclass, field


@dataclass
class TrimConfig:
    """Configuration of map trimming."""

    left: float = 0
    right: float = 0
    top: float = 0
    bottom: float = 0


@dataclass
class ImageConfig:
    """Configuration of map dimensions."""

    scale: float = 1
    rotate: float = 0
    trim: TrimConfig = field(default_factory=TrimConfig)
