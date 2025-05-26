import base64
import logging
import math
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from covgen.util.color_analysis import find_dominant_color

log = logging.getLogger('covgen')


class SimpleTitleGeneration(object):
    def __init__(self, title: str, base64_image: str,
                 title_color: tuple | None, title_font: str,
                 title_height_correction: float = 0.):
        self._title = title
        self._base64_image = base64_image
        self._title_color = title_color
        self._title_font = title_font
        self._title_height_correction = - title_height_correction
        if self._title_color is None:
            _dominant_color = find_dominant_color(b64_image=base64_image)
            _dominant_color = np.minimum(_dominant_color, 255)
            self._title_color = tuple(_dominant_color.tolist())
        log.debug(f'title_color: {self._title_color}')

    @staticmethod
    def pillow_image_to_b64(image: Image) -> str:
        buffered = BytesIO()
        image.save(buffered, format='PNG')
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def generate(self) -> str:
        base_image = Image.open(fp=BytesIO(base64.b64decode(self._base64_image))).convert('RGBA')
        size = base_image.size
        text_size = 9 * size[0] // 10, size[1] // 2
        image_center_coordinate = size[0] / 2, size[1] / 2
        text_box_coordinate = (math.floor(image_center_coordinate[0] - text_size[0] / 2),
                               math.floor(self._title_height_correction +
                                          image_center_coordinate[1] - text_size[1] / 2))
        text_background_color = 255, 255, 255, 0
        text_image = Image.new('RGBA', text_size, text_background_color)
        text_draw = ImageDraw.Draw(text_image)
        font_size = min_font_size = 0
        max_font_size = size[0]
        factor = 10
        for fz in range(max_font_size * factor, min_font_size * factor - 1, -1):
            _fz = fz / factor
            font = ImageFont.truetype(font=self._title_font, size=_fz)
            max_len_line = self._title
            if '\n' in self._title:
                max_len_line = sorted(self._title.splitlines(keepends=False), key=len, reverse=True)[0]
            _text_width = text_draw.textlength(text=max_len_line, font=font)
            if _text_width <= text_size[0]:
                font_size = _fz
                break
        log.debug(f'cover_imitation_fontsize: {font_size}')
        x, y = 0, 0
        font = ImageFont.truetype(font=self._title_font, size=font_size)
        for line in self._title.splitlines(keepends=False):
            text_draw.text(xy=(x, y), text=line, fill=self._title_color, font=font)
            y += font.getbbox(line)[3]
        base_image.paste(im=text_image, box=text_box_coordinate, mask=text_image)
        return self.pillow_image_to_b64(base_image)
