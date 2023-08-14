"""Base class for a map parser."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from .config.color import ColorsPalette
from .config.drawable import Drawable
from .config.image_config import ImageConfig
from .config.size import Sizes
from .config.text import Text
from .image_generator import ImageGenerator
from .map_data import ImageData, MapData

_LOGGER = logging.getLogger(__name__)


class MapDataParser(ABC):
    """Base class for a map parser."""

    def __init__(
        self,
        palette: ColorsPalette,
        sizes: Sizes,
        drawables: list[Drawable],
        image_config: ImageConfig,
        texts: list[Text],
    ):
        self._palette = palette
        self._sizes = sizes
        self._image_config = image_config
        self._texts = texts
        self._image_generator = ImageGenerator(
            palette, sizes, drawables, image_config, texts
        )

    def create_empty(self, text: str) -> MapData:
        map_data = MapData()
        empty_map = self._image_generator.create_empty_map_image(text)
        map_data.image = ImageData.create_empty(empty_map)
        return map_data

    @abstractmethod
    def parse(self, raw: bytes, *args: Any, **kwargs: Any) -> MapData:
        pass

    @abstractmethod
    def unpack_map(self, raw_encoded: bytes, *args: Any, **kwargs: Any) -> bytes:
        pass
