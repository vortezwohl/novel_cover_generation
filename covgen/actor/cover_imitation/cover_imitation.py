import json
import logging

from volcenginesdkarkruntime._exceptions import ArkBadRequestError

from covgen.actor import ark_image_model, ark_client
from covgen.actor.image_understanding.image_understanding import ImageUnderstanding

log = logging.getLogger('covgen')


class CoverImitation(object):
    def __init__(self, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstanding(
            base64_image=base64_image,
            image_format=image_format
        ).image_features()
        log.debug(f'cover_imitation_prompt: {self._prompt}')

    def generate(self, size: tuple = (720, 960)) -> str:
        while True:
            try:
                return ark_client.images.generate(
                    model=ark_image_model,
                    prompt=json.dumps(self._prompt, ensure_ascii=False)
                    + '\n注意: 1.请避免生成NSFW和地缘政治内容. 2.请避免生成任何文字.',
                    size=f'{size[0]}x{size[1]}',
                    response_format='b64_json',
                    watermark=False,
                    guidance_scale=4.5
                ).data[0].b64_json
            except ArkBadRequestError as e:
                log.error(e)
                continue
