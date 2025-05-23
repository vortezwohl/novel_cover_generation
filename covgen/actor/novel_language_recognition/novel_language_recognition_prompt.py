from covgen.common.base_prompt import BasePrompt


class NovelLanguageRecognitionPrompt(BasePrompt):
    def __init__(self, title: str, novel: str):
        super().__init__()
        self._novel = novel
        self._title = title
        self._prompt = {
            '小说标题': title,
            '小说全文': novel[:2048],
            '你是': '一个擅长各国语言的翻译家',
            '目标': '你需要仔细阅读[小说原文]与[小说标题], 然后识别出[小说标题]所使用的语言',
            '可选语言': ['zh', 'en'],
            '输出规范': {
                '输出格式': 'json',
                '输出限制': '语言的可选取值参见[可选语言], 输出不允许超出已知取值范围.',
                '输出示例': {
                    'chain_of_thought': '<在这里给出你的思考过程, 4000字>',
                    'output': '语言为: ...'
                }
            },
            '输出开始': '你的输出以 "语言为: " 正式开始.'
        }

    @property
    def message(self) -> list:
        return [{
            'role': 'system',
            'content': '你的输出请遵循正确合法的 JSON 格式'
        }, {
            'role': 'user',
            'content': [{
                    'type': 'text',
                    'text': self.prompt
                }
            ]
        }]
