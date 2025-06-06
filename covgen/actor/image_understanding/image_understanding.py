import json
import logging

from covgen.util.hash import md5
from covgen.actor import ark_language_model, ark_client
from covgen.actor.image_understanding.image_understanding_prompt import ImageUnderstandingPrompt

log = logging.getLogger('covgen')
CACHE = dict()


class ImageUnderstanding(object):
    def __init__(self, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstandingPrompt(base64_image=base64_image, image_format=image_format)
        self._msg_hash = md5(json.dumps(self._prompt.message_with_image))

    def image_features(self) -> str:
        if self._msg_hash in CACHE.keys():
            decr = CACHE[self._msg_hash]
            log.debug(f'image_with_text_understanding_cache: {decr}')
            return decr
        while True:
            try:
                decr = ark_client.chat.completions.create(
                    model=ark_language_model,
                    messages=self._prompt.message_with_image,
                    temperature=0.2,
                    top_p=0.3
                ).choices[0].message.content
                decr = json.loads(decr).get('output')
                log.debug(f'image_understanding: {decr}')
                CACHE[self._msg_hash] = decr
                return decr
            except json.decoder.JSONDecodeError as e:
                log.error(e)
                continue
