import json

from covgen.actor import ark_language_model, ark_client
from covgen.actor.image_understanding.image_understanding_prompt import ImageUnderstandingPrompt


class ImageUnderstanding(object):
    def __init__(self, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstandingPrompt(base64_image=base64_image, image_format=image_format)

    def image_features(self, max_retries: int = 5) -> dict | None:
        _retries = 0
        outer_keys = ['chain_of_thought', 'output']
        while True:
            if _retries >= max_retries:
                return None
            try:
                resp = ark_client.chat.completions.create(
                    model=ark_language_model,
                    messages=self._prompt.message_with_image,
                    temperature=0.1,
                    top_p=0.1
                ).choices[0].message.content
                resp_dict = json.loads(resp)
                for o_k in outer_keys:
                    if o_k not in resp_dict.keys():
                        continue
                output_dict = resp_dict['output']
                return output_dict
            except json.decoder.JSONDecodeError:
                continue
            finally:
                _retries += 1
