import json
import logging

from volcenginesdkarkruntime._exceptions import ArkBadRequestError

from covgen.actor import ark_image_model, ark_client
from covgen.actor.image_understanding.image_with_text_understanding import ImageWithTextUnderstanding

log = logging.getLogger('covgen')


class DiffuserTitledCoverGeneration(object):
    def __init__(self, title: str, base64_image: str, image_format: str):
        self._title = title
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageWithTextUnderstanding(
            base64_image=base64_image,
            image_format=image_format
        ).image_features()
        if isinstance(self._prompt, dict) or isinstance(self._prompt, list):
            self._prompt = json.dumps(self._prompt, ensure_ascii=False)
        self._prompt = (self._prompt
                        .replace('\",', '; ')
                        .replace('\'', '')
                        .replace('\"', '')
                        .replace('’', '')
                        .replace('“', '')
                        .replace('”', ''))
        self._prompt = (f'"{self._title}" 是书封的书名. 你生成的书封图必须带有书名文字, 且不能有其他任何冗余文字.\n'
                        + '注意: 请避免生成裸露和地缘政治内容.\n'
                        + f'书封图描述: {self._prompt}')
        log.debug(f'diffuser_titled_cover_generation_prompt: {self._prompt}')

    def generate(self, size: tuple = (720, 960)) -> str:
        while True:
            try:
                return ark_client.images.generate(
                    model=ark_image_model,
                    prompt=self._prompt,
                    size=f'{size[0]}x{size[1]}',
                    response_format='b64_json',
                    watermark=False,
                    guidance_scale=4.5
                ).data[0].b64_json
            except ArkBadRequestError as e:
                log.error(e)
                continue
