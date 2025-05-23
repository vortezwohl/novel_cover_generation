import json
import logging

from covgen.actor import ark_client, ark_language_model
from covgen.actor.novel_theme_recognition.novel_theme_recognition_prompt import NovelThemeRecognitionPrompt
from covgen.enum.region import Region
from covgen.enum.subject import Subject

log = logging.getLogger('covgen')


class NovelThemeRecognition(object):
    def __init__(self, novel: str):
        self._prompt = NovelThemeRecognitionPrompt(novel=novel)

    def recognize(self):
        subject = None
        region = None
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
                if '欧美' in decr:
                    region = Region.Western
                elif '东南亚' in decr:
                    region = Region.SouthEastAsia
                else:
                    region = Region.EastAsia
                if '现代言' in decr:
                    subject = Subject.modern_romance
                elif '古代言' in decr:
                    subject = Subject.modern_romance
                else:
                    subject = Subject.werewolves
                return subject, region
            except json.decoder.JSONDecodeError as e:
                log.error(e)
                continue
