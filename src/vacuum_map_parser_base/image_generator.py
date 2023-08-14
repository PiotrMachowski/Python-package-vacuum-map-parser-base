"""Generates a map image."""

import logging
import math
from typing import Callable

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as ImageType
from PIL.Image import Resampling, Transpose
from PIL.ImageDraw import ImageDraw as ImageDrawType

from .config.color import Color, ColorsPalette, SupportedColor
from .config.drawable import Drawable
from .config.image_config import ImageConfig
from .config.size import Size, Sizes
from .config.text import Text
from .map_data import Area, ImageData, MapData, Obstacle, Path, Point

_LOGGER = logging.getLogger(__name__)


class ImageGenerator:
    """Generates a map image."""

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
        self._drawables = drawables
        self._image_config = image_config
        self._texts = texts

    def draw_map(self, map_data: MapData) -> None:
        if map_data.image is None:
            return
        for drawable in self._drawables:
            match drawable:
                case Drawable.CHARGER.value:
                    self._draw_charger(map_data)
                case Drawable.VACUUM_POSITION.value:
                    self._draw_vacuum_position(map_data)
                case Drawable.OBSTACLES.value:
                    self._draw_obstacles(map_data)
                case Drawable.IGNORED_OBSTACLES.value:
                    self._draw_ignored_obstacles(map_data)
                case Drawable.OBSTACLES_WITH_PHOTO.value:
                    self._draw_obstacles_with_photo(map_data)
                case Drawable.IGNORED_OBSTACLES_WITH_PHOTO.value:
                    self._draw_ignored_obstacles_with_photo(map_data)
                case Drawable.MOP_PATH.value:
                    self._draw_mop_path(map_data)
                case Drawable.PATH.value:
                    self._draw_vacuum_path(map_data)
                case Drawable.GOTO_PATH.value:
                    self._draw_goto_path(map_data)
                case Drawable.PREDICTED_PATH.value:
                    self._draw_predicted_path(map_data)
                case Drawable.NO_CARPET_AREAS.value:
                    self._draw_no_carpet_areas(map_data)
                case Drawable.NO_GO_AREAS.value:
                    self._draw_no_go_areas(map_data)
                case Drawable.NO_MOPPING_AREAS.value:
                    self._draw_no_mopping_areas(map_data)
                case Drawable.VIRTUAL_WALLS.value:
                    self._draw_walls(map_data)
                case Drawable.ZONES.value:
                    self._draw_zones(map_data)
                case Drawable.CLEANED_AREA.value:
                    self._draw_layer(map_data, drawable)
                case Drawable.ROOM_NAMES.value:
                    self._draw_room_names(map_data)
        self._rotate(map_data.image)
        self._draw_texts(map_data.image, self._texts)

    def create_empty_map_image(self, text: str = "NO MAP") -> ImageType:
        color = self._get_color(SupportedColor.MAP_OUTSIDE)
        image = Image.new("RGBA", (300, 200), color=color)
        if sum(color[0:3]) > 382:
            text_color = (0, 0, 0)
        else:
            text_color = (255, 255, 255)
        draw = ImageDraw.Draw(image, "RGBA")
        l, t, r, b = draw.textbbox((0, 0), text)
        w, h = r - l, b - t
        draw.text(
            ((image.size[0] - w) / 2, (image.size[1] - h) / 2), text, fill=text_color
        )
        return image

    def _draw_vacuum_path(self, map_data: MapData) -> None:
        if map_data.path is not None and map_data.image is not None:
            self._draw_path(
                map_data.image,
                map_data.path,
                self._get_size(Size.PATH_WIDTH),
                self._get_color(SupportedColor.PATH),
            )

    def _draw_goto_path(self, map_data: MapData) -> None:
        if map_data.goto_path is not None and map_data.image is not None:
            self._draw_path(
                map_data.image,
                map_data.goto_path,
                self._get_size(Size.PATH_WIDTH),
                self._get_color(SupportedColor.GOTO_PATH),
            )

    def _draw_predicted_path(self, map_data: MapData) -> None:
        if map_data.predicted_path is not None and map_data.image is not None:
            self._draw_path(
                map_data.image,
                map_data.predicted_path,
                self._get_size(Size.PATH_WIDTH),
                self._get_color(SupportedColor.PREDICTED_PATH),
            )

    def _draw_mop_path(self, map_data: MapData) -> None:
        if map_data.mop_path is not None and map_data.image is not None:
            self._draw_path(
                map_data.image,
                map_data.mop_path,
                self._get_size(Size.MOP_PATH_WIDTH),
                self._get_color(SupportedColor.MOP_PATH),
            )

    def _draw_no_carpet_areas(self, map_data: MapData) -> None:
        if map_data.no_carpet_areas is not None and map_data.image is not None:
            ImageGenerator._draw_areas(
                map_data.image,
                map_data.no_carpet_areas,
                self._get_color(SupportedColor.NO_CARPET_ZONES),
                self._get_color(SupportedColor.NO_CARPET_ZONES_OUTLINE),
            )

    def _draw_no_go_areas(self, map_data: MapData) -> None:
        if map_data.no_go_areas is not None and map_data.image is not None:
            ImageGenerator._draw_areas(
                map_data.image,
                map_data.no_go_areas,
                self._get_color(SupportedColor.NO_GO_ZONES),
                self._get_color(SupportedColor.NO_GO_ZONES_OUTLINE),
            )

    def _draw_no_mopping_areas(self, map_data: MapData) -> None:
        if map_data.no_mopping_areas is not None and map_data.image is not None:
            ImageGenerator._draw_areas(
                map_data.image,
                map_data.no_mopping_areas,
                self._get_color(SupportedColor.NO_MOPPING_ZONES),
                self._get_color(SupportedColor.NO_MOPPING_ZONES_OUTLINE),
            )

    def _draw_walls(self, map_data: MapData) -> None:
        if map_data.walls is None or map_data.image is None:
            return
        image = map_data.image
        walls = map_data.walls
        color = self._get_color(SupportedColor.VIRTUAL_WALLS)

        def draw_func(draw: ImageDrawType) -> None:
            for wall in walls:
                draw.line(wall.to_img(image.dimensions).as_list(), color, width=2)

        ImageGenerator._draw_on_new_layer(
            image, draw_func, 1, ImageGenerator._use_transparency(color)
        )

    def _draw_zones(self, map_data: MapData) -> None:
        if map_data.zones is None or map_data.image is None:
            return
        ImageGenerator._draw_areas(
            map_data.image,
            [z.as_area() for z in map_data.zones],
            self._get_color(SupportedColor.ZONES),
            self._get_color(SupportedColor.ZONES_OUTLINE),
        )

    def _draw_charger(self, map_data: MapData) -> None:
        if map_data.charger is None or map_data.image is None:
            return
        fill = self._get_color(SupportedColor.CHARGER)
        outline = self._get_color(SupportedColor.CHARGER_OUTLINE)
        radius = self._get_size(Size.CHARGER_RADIUS)
        ImageGenerator._draw_pieslice(
            map_data.image, map_data.charger, radius, outline, fill
        )

    def _draw_obstacles(self, map_data: MapData) -> None:
        if map_data.obstacles is None or map_data.image is None:
            return
        color = self._get_color(SupportedColor.OBSTACLE)
        radius = self._get_size(Size.OBSTACLE_RADIUS)
        ImageGenerator._draw_all_obstacles(
            map_data.image, map_data.obstacles, radius, color
        )

    def _draw_ignored_obstacles(self, map_data: MapData) -> None:
        if map_data.ignored_obstacles is None or map_data.image is None:
            return
        color = self._get_color(SupportedColor.IGNORED_OBSTACLE)
        radius = self._get_size(Size.IGNORED_OBSTACLE_RADIUS)
        ImageGenerator._draw_all_obstacles(
            map_data.image, map_data.ignored_obstacles, radius, color
        )

    def _draw_obstacles_with_photo(self, map_data: MapData) -> None:
        if map_data.obstacles_with_photo is None or map_data.image is None:
            return
        color = self._get_color(SupportedColor.OBSTACLE_WITH_PHOTO)
        radius = self._get_size(Size.OBSTACLE_WITH_PHOTO_RADIUS)
        ImageGenerator._draw_all_obstacles(
            map_data.image, map_data.obstacles_with_photo, radius, color
        )

    def _draw_ignored_obstacles_with_photo(self, map_data: MapData) -> None:
        if map_data.ignored_obstacles_with_photo is None or map_data.image is None:
            return
        color = self._get_color(SupportedColor.IGNORED_OBSTACLE_WITH_PHOTO)
        radius = self._get_size(Size.IGNORED_OBSTACLE_WITH_PHOTO_RADIUS)
        ImageGenerator._draw_all_obstacles(
            map_data.image, map_data.ignored_obstacles_with_photo, radius, color
        )

    def _draw_vacuum_position(self, map_data: MapData) -> None:
        if map_data.vacuum_position is None or map_data.image is None:
            return
        color = self._get_color(SupportedColor.ROBO)
        outline = self._get_color(SupportedColor.ROBO_OUTLINE)
        radius = self._get_size(Size.VACUUM_RADIUS)
        ImageGenerator._draw_vacuum(
            map_data.image, map_data.vacuum_position, radius, outline, color
        )

    def _draw_room_names(self, map_data: MapData) -> None:
        if map_data.rooms is None or map_data.image is None:
            return
        color = self._get_color(SupportedColor.ROOM_NAMES)
        for room in map_data.rooms.values():
            p = room.point()
            if p is not None and room.name is not None:
                point = p.to_img(map_data.image.dimensions)
                self._draw_text(map_data.image, room.name, point.x, point.y, color)

    def _rotate(self, image: ImageData) -> None:
        if image.dimensions.rotation == 90:
            image.data = image.data.transpose(Transpose.ROTATE_90)
        elif image.dimensions.rotation == 180:
            image.data = image.data.transpose(Transpose.ROTATE_180)
        elif image.dimensions.rotation == 270:
            image.data = image.data.transpose(Transpose.ROTATE_270)
        else:
            image.data = image.data.rotate(
                image.dimensions.rotation,
                Resampling.BILINEAR,
                True,
                fillcolor=self._get_color(SupportedColor.MAP_OUTSIDE),
            )

    @staticmethod
    def _draw_texts(image: ImageData, texts: list[Text]) -> None:
        for text_config in texts:
            x = text_config.x * image.data.size[0] / 100
            y = text_config.y * image.data.size[1] / 100
            ImageGenerator._draw_text(
                image,
                text_config.text,
                x,
                y,
                text_config.color,
                text_config.font,
                text_config.font_size,
            )

    @staticmethod
    def _draw_layer(map_data: MapData, layer_name: str) -> None:
        if (
            map_data.image is not None
            and layer_name in map_data.image.additional_layers
        ):
            ImageGenerator._draw_layer_with_alpha(
                map_data.image, map_data.image.additional_layers[layer_name]
            )

    @staticmethod
    def _draw_all_obstacles(
        image: ImageData, obstacles: list[Obstacle], radius: float, color: Color
    ) -> None:
        for obstacle in obstacles:
            ImageGenerator._draw_circle(image, obstacle, radius, color, color)

    def _get_color(self, name: SupportedColor) -> Color:
        return self._palette.get_color(name)

    def _get_room_color(self, index: int) -> Color:
        return self._palette.get_room_color(index + 1)

    def _get_size(self, size: Size) -> float:
        return self._sizes.get_size(size)

    @staticmethod
    def _use_transparency(*colors: Color) -> bool:
        return any(len(color) > 3 for color in colors)

    @staticmethod
    def _draw_vacuum(
        image: ImageData, vacuum_pos: Point, r: float, outline: Color, fill: Color
    ) -> None:
        def draw_func(draw: ImageDrawType) -> None:
            if vacuum_pos.a is None:
                vacuum_pos.a = 0
            point = vacuum_pos.to_img(image.dimensions)
            r_scaled = r / 16
            # main outline
            coords = [point.x - r, point.y - r, point.x + r, point.y + r]
            draw.ellipse(coords, outline=outline, fill=fill)
            if r >= 8:
                # secondary outline
                r2 = r_scaled * 14
                x = point.x
                y = point.y
                coords = [x - r2, y - r2, x + r2, y + r2]
                draw.ellipse(coords, outline=outline)
            # bin cover
            a1 = (vacuum_pos.a + 104) / 180 * math.pi
            a2 = (vacuum_pos.a - 104) / 180 * math.pi
            r2 = r_scaled * 13
            x1 = point.x - r2 * math.cos(a1)
            y1 = point.y + r2 * math.sin(a1)
            x2 = point.x - r2 * math.cos(a2)
            y2 = point.y + r2 * math.sin(a2)
            draw.line([x1, y1, x2, y2], width=1, fill=outline)
            # lidar
            angle = vacuum_pos.a / 180 * math.pi
            r2 = r_scaled * 3
            x = point.x + r2 * math.cos(angle)
            y = point.y - r2 * math.sin(angle)
            r2 = r_scaled * 4
            coords = [x - r2, y - r2, x + r2, y + r2]
            draw.ellipse(coords, outline=outline, fill=fill)
            # button
            half_color = (
                (outline[0] + fill[0]) // 2,
                (outline[1] + fill[1]) // 2,
                (outline[2] + fill[2]) // 2,
            )
            r2 = r_scaled * 10
            x = point.x + r2 * math.cos(angle)
            y = point.y - r2 * math.sin(angle)
            r2 = r_scaled * 2
            coords = [x - r2, y - r2, x + r2, y + r2]
            draw.ellipse(coords, outline=half_color, fill=half_color)

        ImageGenerator._draw_on_new_layer(
            image, draw_func, 1, ImageGenerator._use_transparency(outline, fill)
        )

    @staticmethod
    def _draw_circle(
        image: ImageData, center: Point, r: float, outline: Color, fill: Color
    ) -> None:
        def draw_func(draw: ImageDrawType) -> None:
            point = center.to_img(image.dimensions)
            coords = [point.x - r, point.y - r, point.x + r, point.y + r]
            draw.ellipse(coords, outline=outline, fill=fill)

        ImageGenerator._draw_on_new_layer(
            image, draw_func, 1, ImageGenerator._use_transparency(outline, fill)
        )

    @staticmethod
    def _draw_pieslice(
        image: ImageData, position: Point, r: float, outline: Color, fill: Color
    ) -> None:
        def draw_func(draw: ImageDrawType) -> None:
            point = position.to_img(image.dimensions)
            angle = -position.a if position.a is not None else 0
            coords = (point.x - r, point.y - r), (point.x + r, point.y + r)
            draw.pieslice(coords, angle + 90, angle - 90, outline=outline, fill=fill)

        ImageGenerator._draw_on_new_layer(
            image, draw_func, 1, ImageGenerator._use_transparency(outline, fill)
        )

    @staticmethod
    def _draw_areas(
        image: ImageData, areas: list[Area], fill: Color, outline: Color
    ) -> None:
        if len(areas) == 0:
            return

        use_transparency = ImageGenerator._use_transparency(outline, fill)
        for area in areas:
            polygon = area.to_img(image.dimensions).as_list()

            def draw_func(draw: ImageDrawType) -> None:
                draw.polygon(polygon, fill, outline)

            ImageGenerator._draw_on_new_layer(image, draw_func, 1, use_transparency)

    def _draw_path(
        self, image: ImageData, path: Path, path_width: float, color: Color
    ) -> None:
        if len(path.path) < 1:
            return

        scale = self._image_config.scale

        def draw_func(draw: ImageDrawType) -> None:
            for current_path in path.path:
                if len(current_path) > 1:
                    s = current_path[0].to_img(image.dimensions) * scale
                    coords = None
                    for point in current_path[1:]:
                        e = point.to_img(image.dimensions) * scale
                        draw.line(
                            [s.x, s.y, e.x, e.y],
                            width=int(scale * path_width),
                            fill=color,
                        )
                        if path_width > 4:
                            r = scale * path_width / 2
                            if not coords:
                                coords = (s.x - r, s.y - r), (s.x + r, s.y + r)
                                draw.pieslice(coords, 0, 360, outline=color, fill=color)
                            coords = (e.x - r, e.y - r), (e.x + r, e.y + r)
                            draw.pieslice(coords, 0, 360, outline=color, fill=color)
                        s = e

        ImageGenerator._draw_on_new_layer(
            image, draw_func, scale, ImageGenerator._use_transparency(color)
        )

    @staticmethod
    def _draw_text(
        image: ImageData,
        text: str,
        x: float,
        y: float,
        color: Color,
        font_file: str | None = None,
        font_size: int | None = None,
    ) -> None:
        def draw_func(draw: ImageDrawType) -> None:
            font = None
            try:
                if font_file is not None and font_size is not None and font_size > 0:
                    font = ImageFont.truetype(font_file, font_size)
            except OSError:
                _LOGGER.warning("Unable to find font file: %s", font_file)
            except ImportError:
                _LOGGER.warning("Unable to open font: %s", font_file)
            finally:
                l, t, r, b = draw.textbbox((0, 0), text, font)
                w, h = r - l, b - t
                draw.text((x - w / 2, y - h / 2), text, font=font, fill=color)

        ImageGenerator._draw_on_new_layer(
            image, draw_func, 1, ImageGenerator._use_transparency(color)
        )

    @staticmethod
    def _draw_on_new_layer(
        image: ImageData,
        draw_function: Callable[[ImageDrawType], None],
        scale: float = 1,
        use_transparency: bool = False,
    ) -> None:
        if scale == 1 and not use_transparency:
            draw = ImageDraw.Draw(image.data, "RGBA")
            draw_function(draw)
        else:
            size = (int(image.data.size[0] * scale), int(image.data.size[1] * scale))
            layer = Image.new("RGBA", size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(layer, "RGBA")
            draw_function(draw)
            if scale != 1:
                layer = layer.resize(image.data.size, resample=Resampling.BOX)
            ImageGenerator._draw_layer_with_alpha(image, layer)

    @staticmethod
    def _draw_layer_with_alpha(image: ImageData, layer: ImageType) -> None:
        image.data = Image.alpha_composite(image.data, layer)
