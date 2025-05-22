import json


class BasePrompt:
    def __init__(self):
        self._prompt = str()

    @property
    def prompt(self) -> str:
        if isinstance(self._prompt, dict):
            return json.dumps(self._prompt, ensure_ascii=False)
        return self._prompt

    def __str__(self):
        return self.prompt

    def __repr__(self):
        return self.__str__()
