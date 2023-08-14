"""Contains classes that are returned as a result of parsing."""

from __future__ import annotations

import math
from abc import ABC
from dataclasses import asdict, dataclass
from typing import Any, Callable

from PIL.Image import Image as ImageType

from .config.image_config import ImageConfig

CalibrationPoints = list[dict[str, dict[str, float | int]]]


@dataclass
class OutputObject(ABC):
    """Base class for parsing outcomes."""

    def as_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Point(OutputObject):
    """Point on a map."""

    x: float
    y: float
    a: float | None = None

    def to_img(self, image_dimensions: ImageDimensions) -> Point:
        return image_dimensions.to_img(self)

    def rotated(self, image_dimensions: ImageDimensions) -> Point:
        alpha = image_dimensions.rotation
        w = int(image_dimensions.width * image_dimensions.scale)
        h = int(image_dimensions.height * image_dimensions.scale)
        x = self.x
        y = self.y
        if alpha % 90 == 0:
            while alpha > 0:
                (x, y) = (y, w - x)
                (h, w) = (w, h)
                alpha = alpha - 90
            return Point(x, y)
        xm = w / 2
        ym = h / 2
        a = math.radians(alpha)
        wr = math.fabs(w * math.cos(a)) + math.fabs(h * math.sin(a))
        hr = math.fabs(w * math.sin(a)) + math.fabs(h * math.cos(a))
        xr = (x - xm) * math.cos(a) + (y - ym) * math.sin(a) + wr / 2
        yr = -(x - xm) * math.sin(a) + (y - ym) * math.cos(a) + hr / 2
        return Point(xr, yr)

    def __mul__(self, other: float) -> Point:
        return Point(self.x * other, self.y * other, self.a)

    def __truediv__(self, other: float) -> Point:
        return Point(self.x / other, self.y / other, self.a)


@dataclass
class Obstacle(Point):
    """Obstacle on a map."""

    def __init__(self, x: float, y: float, details: ObstacleDetails):
        super().__init__(x, y)
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        return {**super().as_dict(), **self.details.as_dict()}


@dataclass
class ObstacleDetails(OutputObject):
    """Metadata of an obstacle."""

    type: int | None = None
    description: str | None = None
    confidence_level: float | None = None
    photo_name: str | None = None


@dataclass
class ImageDimensions:
    """Dimensions of an image."""

    top: int
    left: int
    height: int
    width: int
    scale: float
    rotation: float
    img_transformation: Callable[[Point], Point]

    def to_img(self, point: Point) -> Point:
        p = self.img_transformation(point)
        return Point(
            (p.x - self.left) * self.scale,
            (self.height - (p.y - self.top) - 1) * self.scale,
        )


class ImageData(OutputObject):
    """Image data."""

    def __init__(
        self,
        size: int,
        top: int,
        left: int,
        height: int,
        width: int,
        image_config: ImageConfig,
        data: ImageType,
        img_transformation: Callable[[Point], Point],
        additional_layers: dict[str, ImageType | None] | None = None,
    ):
        trim_left = int(image_config.trim.left * width / 100)
        trim_right = int(image_config.trim.right * width / 100)
        trim_top = int(image_config.trim.top * height / 100)
        trim_bottom = int(image_config.trim.bottom * height / 100)
        scale = image_config.scale
        rotation = image_config.rotate
        self.size = size
        self.dimensions = ImageDimensions(
            top + trim_bottom,
            left + trim_left,
            height - trim_top - trim_bottom,
            width - trim_left - trim_right,
            scale,
            rotation,
            img_transformation,
        )
        self.is_empty = height == 0 or width == 0
        self.data = data
        self.additional_layers: dict[str, ImageType] = (
            {}
            if additional_layers is None
            else {
                name: layer
                for name, layer in additional_layers.items()
                if layer is not None
            }
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "size": self.size,
            "offset_y": self.dimensions.top,
            "offset_x": self.dimensions.left,
            "height": self.dimensions.height,
            "scale": self.dimensions.scale,
            "rotation": self.dimensions.rotation,
            "width": self.dimensions.width,
        }

    @staticmethod
    def create_empty(data: ImageType) -> ImageData:
        return ImageData(0, 0, 0, 0, 0, ImageConfig(), data, lambda p: p)


@dataclass
class Path(OutputObject):
    """Path on a map."""

    point_length: int | None
    point_size: int | None
    angle: int | None
    path: list[list[Point]]

    def as_dict(self) -> dict[str, Any]:
        return {
            **super().as_dict(),
            "path": [[p.as_dict() for p in subpath] for subpath in self.path],
        }


@dataclass
class Zone(OutputObject):
    """Zone on a map."""

    x0: float
    y0: float
    x1: float
    y1: float

    def as_area(self) -> Area:
        return Area(
            self.x0, self.y0, self.x0, self.y1, self.x1, self.y1, self.x1, self.y0
        )


@dataclass
class Room(Zone):
    """Room on a map."""

    number: int
    name: str | None = None
    pos_x: float | None = None
    pos_y: float | None = None

    def point(self) -> Point | None:
        if self.pos_x is not None and self.pos_y is not None and self.name is not None:
            return Point(self.pos_x, self.pos_y)
        return None


@dataclass
class Wall(OutputObject):
    """Wall on a map."""

    x0: float
    y0: float
    x1: float
    y1: float

    def to_img(self, image_dimensions: ImageDimensions) -> Wall:
        p0 = Point(self.x0, self.y0).to_img(image_dimensions)
        p1 = Point(self.x1, self.y1).to_img(image_dimensions)
        return Wall(p0.x, p0.y, p1.x, p1.y)

    def as_list(self) -> list[float]:
        return [self.x0, self.y0, self.x1, self.y1]


@dataclass
class Area(OutputObject):
    """Area on a map."""

    x0: float
    y0: float
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float

    def as_list(self) -> list[float]:
        return [self.x0, self.y0, self.x1, self.y1, self.x2, self.y2, self.x3, self.y3]

    def to_img(self, image_dimensions: ImageDimensions) -> Area:
        p0 = Point(self.x0, self.y0).to_img(image_dimensions)
        p1 = Point(self.x1, self.y1).to_img(image_dimensions)
        p2 = Point(self.x2, self.y2).to_img(image_dimensions)
        p3 = Point(self.x3, self.y3).to_img(image_dimensions)
        return Area(p0.x, p0.y, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)


class MapData:
    """Parsed map data."""

    def __init__(self, calibration_center: float = 0, calibration_diff: float = 0):
        self._calibration_center = calibration_center
        self._calibration_diff = calibration_diff
        self.blocks = None
        self.charger: Point | None = None
        self.goto: list[Point] | None = None
        self.goto_path: Path | None = None
        self.image: ImageData | None = None
        self.no_go_areas: list[Area] | None = None
        self.no_mopping_areas: list[Area] | None = None
        self.no_carpet_areas: list[Area] | None = None
        self.carpet_map: set[int] | None = set()
        self.obstacles: list[Obstacle] | None = None
        self.ignored_obstacles: list[Obstacle] | None = None
        self.obstacles_with_photo: list[Obstacle] | None = None
        self.ignored_obstacles_with_photo: list[Obstacle] | None = None
        self.path: Path | None = None
        self.predicted_path: Path | None = None
        self.mop_path: Path | None = None
        self.rooms: dict[int, Room] | None = None
        self.vacuum_position: Point | None = None
        self.vacuum_room: int | None = None
        self.vacuum_room_name: str | None = None
        self.walls: list[Wall] | None = None
        self.zones: list[Zone] | None = None
        self.cleaned_rooms: set[int] | None = None
        self.map_name: str | None = None

    def calibration(self) -> CalibrationPoints | None:
        if self.image is None or self.image.is_empty:
            return None
        calibration_points = []
        for point in [
            Point(self._calibration_center, self._calibration_center),
            Point(
                self._calibration_center + self._calibration_diff * 10,
                self._calibration_center,
            ),
            Point(
                self._calibration_center,
                self._calibration_center + self._calibration_diff * 10,
            ),
        ]:
            img_point = point.to_img(self.image.dimensions).rotated(
                self.image.dimensions
            )
            calibration_points.append(
                {
                    "vacuum": {"x": point.x, "y": point.y},
                    "map": {"x": img_point.x, "y": img_point.y},
                }
            )
        return calibration_points
