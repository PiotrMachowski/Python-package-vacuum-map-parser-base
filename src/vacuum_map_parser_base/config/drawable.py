"""Configuration of elements that can be drawn on a map."""

from enum import StrEnum


class Drawable(StrEnum):
    """Supported element of a map image."""

    CHARGER = "charger"
    CLEANED_AREA = "cleaned_area"
    GOTO_PATH = "goto_path"
    IGNORED_OBSTACLES = "ignored_obstacles"
    IGNORED_OBSTACLES_WITH_PHOTO = "ignored_obstacles_with_photo"
    MOP_PATH = "mop_path"
    NO_CARPET_AREAS = "no_carpet_zones"
    NO_GO_AREAS = "no_go_zones"
    NO_MOPPING_AREAS = "no_mopping_zones"
    OBSTACLES = "obstacles"
    OBSTACLES_WITH_PHOTO = "obstacles_with_photo"
    PATH = "path"
    PREDICTED_PATH = "predicted_path"
    ROOM_NAMES = "room_names"
    VACUUM_POSITION = "vacuum_position"
    VIRTUAL_WALLS = "virtual_walls"
    ZONES = "zones"
