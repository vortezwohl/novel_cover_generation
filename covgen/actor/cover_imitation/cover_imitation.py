import base64
import json
import logging
import math
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from volcenginesdkarkruntime._exceptions import ArkBadRequestError

from covgen.actor import ark_image_model, ark_client
from covgen.actor.image_understanding.image_understanding import ImageUnderstanding

log = logging.getLogger('covgen')


class CoverImitation(object):
    def __init__(self, title: str, base64_image: str,
                 image_format: str, title_color: tuple | str,
                 title_font: str = 'arial.ttf', title_height_correction: float = 0):
        self._title = title
        self._title_font = title_font
        self._title_height_correction = - title_height_correction
        self._title_color = title_color
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstanding(
            base64_image=base64_image,
            image_format=image_format
        ).image_features()
        log.debug(f'cover_imitation_prompt: {self._prompt}')

    def generate(self, size: tuple = (720, 960)) -> Image:
        text_size = 3 * size[0] // 4, size[1] // 10
        image_center_coordinate = size[0] / 2, size[1] / 2
        text_box_coordinate = (math.floor(image_center_coordinate[0] - text_size[0] / 2),
                               math.floor(self._title_height_correction +
                                          image_center_coordinate[1] - text_size[1] / 2))
        text_background_color = 255, 255, 255, 0
        text_image = Image.new('RGBA', text_size, text_background_color)
        text_draw = ImageDraw.Draw(text_image)
        font_size = min_font_size = 0
        max_font_size = size[0]
        factor = 100
        for fz in range(max_font_size * factor, min_font_size * factor - 1, -1):
            _fz = fz / factor
            font = ImageFont.truetype(font=self._title_font, size=_fz)
            _text_width = text_draw.textlength(text=self._title, font=font)
            if _text_width <= text_size[0]:
                font_size = _fz
                break
        print('font size', font_size)
        font = ImageFont.truetype(font=self._title_font, size=font_size)
        text_draw.text(xy=(0, 0), text=self._title, fill=self._title_color, font=font)
        resp = None
        while resp is None:
            try:
                resp = ark_client.images.generate(
                    model=ark_image_model,
                    prompt=json.dumps(self._prompt, ensure_ascii=False) + '\n注意: 请避免生成NSFW和地缘政治内容.',
                    size=f'{size[0]}x{size[1]}',
                    response_format='b64_json',
                    watermark=False,
                    guidance_scale=5
                ).data[0].b64_json
            except ArkBadRequestError as e:
                log.error(e)
                continue
        image_bytes = base64.b64decode(resp)
        _image = Image.open(fp=BytesIO(image_bytes)).convert('RGBA')
        _image.paste(im=text_image, box=text_box_coordinate, mask=text_image)
        return _image


if __name__ == '__main__':
    from covgen.util.image_stringifier import stringify
    image = CoverImitation(title='The Secret I Heard',
                           base64_image=stringify(r'D:\project\covgen\resource\knowledge_base\female_oriented\modern_romance\western_realistic\img_3.png'),
                           image_format='png',
                           title_color='white',
                           title_font=r'D:\project\covgen\resource\font\Gabriola.ttf',
                           title_height_correction=-300
                           ).generate()
    image.save(r'D:\project\covgen\test\output\cover_imitation.png')
