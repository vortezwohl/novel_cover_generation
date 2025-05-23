import json
import logging

from covgen.actor import ark_image_model, ark_client
from covgen.actor.image_understanding.image_understanding import ImageUnderstanding

log = logging.getLogger('covgen')


class CoverImitation(object):
    def __init__(self, title: str, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstanding(
            base64_image=base64_image,
            image_format=image_format
        ).image_features()
        log.debug(f'cover_imitation_prompt: {self._prompt}')

    def generate(self, size: str = '720x960') -> str:
        resp = ark_client.images.generate(
            model=ark_image_model,
            prompt=json.dumps(self._prompt, ensure_ascii=False),
            size=size,
            response_format='url',
            watermark=False,
            guidance_scale=8
        )
        return resp.data[0].url


if __name__ == '__main__':
    from covgen.util.image_stringifier import stringify
    print(CoverImitation('The Secret I Heard in the Operating Room Changed Everything', stringify(r'D:\project\covgen\resource\knowledge_base\female_oriented\modern_romance\western_realistic\img_4.png'), 'png').generate())
