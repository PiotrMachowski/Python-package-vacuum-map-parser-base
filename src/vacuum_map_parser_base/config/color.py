"""Configuration of map colors."""

from __future__ import annotations

from enum import StrEnum
from random import Random
from typing import TypeVar

T = TypeVar("T")
Color = tuple[int, int, int] | tuple[int, int, int, int]


class SupportedColor(StrEnum):
    """Color of a supported map element."""

    CARPETS = "color_carpets"
    CHARGER = "color_charger"
    CHARGER_OUTLINE = "color_charger_outline"
    CLEANED_AREA = "color_cleaned_area"
    GOTO_PATH = "color_goto_path"
    GREY_WALL = "color_grey_wall"
    IGNORED_OBSTACLE = "color_ignored_obstacle"
    IGNORED_OBSTACLE_WITH_PHOTO = "color_ignored_obstacle_with_photo"
    MAP_INSIDE = "color_map_inside"
    MAP_OUTSIDE = "color_map_outside"
    MAP_WALL = "color_map_wall"
    MAP_WALL_V2 = "color_map_wall_v2"
    MOP_PATH = "color_mop_path"
    NEW_DISCOVERED_AREA = "color_new_discovered_area"
    NO_CARPET_ZONES = "color_no_carpet_zones"
    NO_CARPET_ZONES_OUTLINE = "color_no_carpet_zones_outline"
    NO_GO_ZONES = "color_no_go_zones"
    NO_GO_ZONES_OUTLINE = "color_no_go_zones_outline"
    NO_MOPPING_ZONES = "color_no_mop_zones"
    NO_MOPPING_ZONES_OUTLINE = "color_no_mop_zones_outline"
    OBSTACLE = "color_obstacle"
    OBSTACLE_WITH_PHOTO = "color_obstacle_with_photo"
    PATH = "color_path"
    PREDICTED_PATH = "color_predicted_path"
    ROBO = "color_robo"
    ROBO_OUTLINE = "color_robo_outline"
    ROOM_NAMES = "color_room_names"
    SCAN = "color_scan"
    UNKNOWN = "color_unknown"
    VIRTUAL_WALLS = "color_virtual_walls"
    ZONES = "color_zones"
    ZONES_OUTLINE = "color_zones_outline"


class ColorsPalette:
    """Container that simplifies retrieving desired color."""

    COLORS: dict[SupportedColor, Color] = {
        SupportedColor.MAP_INSIDE: (32, 115, 185),
        SupportedColor.MAP_OUTSIDE: (19, 87, 148),
        SupportedColor.MAP_WALL: (100, 196, 254),
        SupportedColor.MAP_WALL_V2: (93, 109, 126),
        SupportedColor.GREY_WALL: (93, 109, 126),
        SupportedColor.CLEANED_AREA: (127, 127, 127, 127),
        SupportedColor.PATH: (147, 194, 238),
        SupportedColor.GOTO_PATH: (0, 255, 0),
        SupportedColor.PREDICTED_PATH: (255, 255, 0),
        SupportedColor.ZONES: (0xAD, 0xD8, 0xFF, 0x8F),
        SupportedColor.ZONES_OUTLINE: (0xAD, 0xD8, 0xFF),
        SupportedColor.VIRTUAL_WALLS: (255, 0, 0),
        SupportedColor.NEW_DISCOVERED_AREA: (64, 64, 64),
        SupportedColor.CARPETS: (0xA9, 0xF7, 0xA9),
        SupportedColor.NO_CARPET_ZONES: (255, 33, 55, 127),
        SupportedColor.NO_CARPET_ZONES_OUTLINE: (255, 0, 0),
        SupportedColor.NO_GO_ZONES: (255, 33, 55, 127),
        SupportedColor.NO_GO_ZONES_OUTLINE: (255, 0, 0),
        SupportedColor.NO_MOPPING_ZONES: (163, 130, 211, 127),
        SupportedColor.NO_MOPPING_ZONES_OUTLINE: (163, 130, 211),
        SupportedColor.CHARGER: (0x66, 0xFE, 0xDA, 0x7F),
        SupportedColor.CHARGER_OUTLINE: (0x66, 0xFE, 0xDA, 0x7F),
        SupportedColor.ROBO: (0xFF, 0xFF, 0xFF),
        SupportedColor.ROBO_OUTLINE: (0, 0, 0),
        SupportedColor.ROOM_NAMES: (0, 0, 0),
        SupportedColor.OBSTACLE: (0, 0, 0, 128),
        SupportedColor.IGNORED_OBSTACLE: (0, 0, 0, 128),
        SupportedColor.OBSTACLE_WITH_PHOTO: (0, 0, 0, 128),
        SupportedColor.IGNORED_OBSTACLE_WITH_PHOTO: (0, 0, 0, 128),
        SupportedColor.UNKNOWN: (0, 0, 0),
        SupportedColor.SCAN: (0xDF, 0xDF, 0xDF),
    }

    ROOM_COLORS: dict[str, Color] = {
        "1": (240, 178, 122),
        "2": (133, 193, 233),
        "3": (217, 136, 128),
        "4": (52, 152, 219),
        "5": (205, 97, 85),
        "6": (243, 156, 18),
        "7": (88, 214, 141),
        "8": (245, 176, 65),
        "9": (252, 212, 81),
        "10": (72, 201, 176),
        "11": (84, 153, 199),
        "12": (133, 193, 233),
        "13": (245, 176, 65),
        "14": (82, 190, 128),
        "15": (72, 201, 176),
        "16": (165, 105, 189),
    }

    def __init__(
        self,
        colors_dict: dict[SupportedColor, Color] | None = None,
        room_colors: dict[str, Color] | None = None,
    ) -> None:
        self._random = Random()
        if colors_dict is None:
            self._overriden_colors = {}
        else:
            self._overriden_colors = colors_dict
        if room_colors is None:
            self._overriden_room_colors = {}
        else:
            self._overriden_room_colors = room_colors

    def get_color(self, color_name: SupportedColor) -> Color:
        return self._overriden_colors.get(
            color_name,
            ColorsPalette.COLORS.get(
                color_name, ColorsPalette.COLORS.get(SupportedColor.UNKNOWN, (0, 0, 0))
            ),
        )

    def get_room_color(self, room_id: str | int) -> Color:
        if isinstance(room_id, str):
            room_id = int(room_id)
        if room_id > len(ColorsPalette.ROOM_COLORS):
            room_id = (room_id - 1) % len(ColorsPalette.ROOM_COLORS) + 1

        key = str(room_id)
        return self._overriden_room_colors.get(
            key,
            ColorsPalette.ROOM_COLORS.get(
                key,
                ColorsPalette.ROOM_COLORS.get(
                    str(self._random.randint(1, 16)), (0, 0, 0)
                ),
            ),
        )
