import logging

from covgen.actor import ark_language_model, ark_client
from covgen.actor.image_understanding.image_understanding_prompt import ImageUnderstandingPrompt

log = logging.getLogger('covgen')


class ImageUnderstanding(object):
    def __init__(self, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstandingPrompt(base64_image=base64_image, image_format=image_format)

    def image_features(self) -> str:
        decr = ark_client.chat.completions.create(
            model=ark_language_model,
            messages=self._prompt.message_with_image,
            temperature=0.1,
            top_p=0.1
        ).choices[0].message.content
        log.debug(f'image_understanding_prompt: {decr}')
        return decr
