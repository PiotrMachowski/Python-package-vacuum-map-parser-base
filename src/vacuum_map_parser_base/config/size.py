"""Configuration of sizes of map elements."""

from enum import StrEnum


class Size(StrEnum):
    """Identifier of a size of a map element."""

    CHARGER_RADIUS = "charger_radius"
    IGNORED_OBSTACLE_RADIUS = "ignored_obstacle_radius"
    IGNORED_OBSTACLE_WITH_PHOTO_RADIUS = "ignored_obstacle_with_photo_radius"
    MOP_PATH_WIDTH = "mop_path_width"
    OBSTACLE_RADIUS = "obstacle_radius"
    OBSTACLE_WITH_PHOTO_RADIUS = "obstacle_with_photo_radius"
    VACUUM_RADIUS = "vacuum_radius"
    PATH_WIDTH = "path_width"


class Sizes:
    """Container that simplifies retrieving size of map elements."""

    SIZES = {
        Size.VACUUM_RADIUS: 6,
        Size.PATH_WIDTH: 1,
        Size.IGNORED_OBSTACLE_RADIUS: 3,
        Size.IGNORED_OBSTACLE_WITH_PHOTO_RADIUS: 3,
        Size.OBSTACLE_RADIUS: 3,
        Size.OBSTACLE_WITH_PHOTO_RADIUS: 3,
        Size.CHARGER_RADIUS: 6,
    }

    def __init__(self, sizes: dict[Size, float] | None = None):
        if sizes is None:
            self._overriden_sizes = {}
        else:
            self._overriden_sizes = sizes

    def get_size(self, size: Size) -> float:
        return self._overriden_sizes.get(size, Sizes.SIZES.get(size, 1))
