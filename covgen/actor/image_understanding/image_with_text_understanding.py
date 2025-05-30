import json
import logging

from covgen.actor import ark_language_model, ark_client
from covgen.actor.image_understanding.image_with_text_understanding_prompt import ImageWithTextUnderstandingPrompt

log = logging.getLogger('covgen')


class ImageWithTextUnderstanding(object):
    def __init__(self, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageWithTextUnderstandingPrompt(base64_image=base64_image, image_format=image_format)

    def image_features(self) -> str:
        while True:
            try:
                decr = ark_client.chat.completions.create(
                    model=ark_language_model,
                    messages=self._prompt.message_with_image,
                    temperature=0.2,
                    top_p=0.3
                ).choices[0].message.content
                decr = json.loads(decr).get('output')
                log.debug(f'image_with_text_understanding: {decr}')
                return decr
            except json.decoder.JSONDecodeError as e:
                log.error(e)
                continue
