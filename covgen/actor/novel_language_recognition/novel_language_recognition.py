import json
import logging

from covgen.actor import ark_client, ark_language_model
from covgen.actor.novel_language_recognition.novel_language_recognition_prompt import NovelLanguageRecognitionPrompt
from covgen.enum.lang import Lang

log = logging.getLogger('covgen')


class NovelLanguageRecognition(object):
    def __init__(self, title: str, novel: str):
        self._prompt = NovelLanguageRecognitionPrompt(title=title, novel=novel)

    def recognize(self):
        lang = None
        while True:
            try:
                decr = ark_client.chat.completions.create(
                    model=ark_language_model,
                    messages=self._prompt.message,
                    temperature=0.1,
                    top_p=0.1
                ).choices[0].message.content
                decr = json.loads(decr).get('output')
                if 'zh' in decr:
                    lang = Lang.Zh
                else:
                    lang = Lang.En
                log.debug(f'novel_language_recognition: {lang}')
                return lang
            except json.decoder.JSONDecodeError as e:
                log.error(e)
                continue
