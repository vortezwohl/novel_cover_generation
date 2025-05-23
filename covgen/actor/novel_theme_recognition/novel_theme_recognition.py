import json
import logging

from covgen.actor import ark_client, ark_language_model
from covgen.actor.novel_theme_recognition.novel_theme_recognition_prompt import NovelThemeRecognitionPrompt

log = logging.getLogger('covgen')


class NovelThemeRecognition(object):
    def __init__(self, novel: str):
        self._prompt = NovelThemeRecognitionPrompt(novel=novel)

    def recognize(self):
        while True:
            try:
                decr = ark_client.chat.completions.create(
                    model=ark_language_model,
                    messages=self._prompt.message,
                    temperature=0.1,
                    top_p=0.1
                ).choices[0].message.content
                decr = json.loads(decr).get('output')
                log.debug(f'novel_theme_recognition_prompt: {decr}')
                return decr
            except json.decoder.JSONDecodeError as e:
                log.error(e)
                continue
