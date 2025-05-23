from covgen.common.base_prompt import BasePrompt


class NovelThemeRecognitionPrompt(BasePrompt):
    def __init__(self, novel: str):
        super().__init__()
        self._novel = novel
        self._prompt = {
            '小说全文': novel[:2048],
            '你是': '一个擅长网络文学作品赏析的网文作家',
            '目标': '你需要分辨出[小说原文]所属主题和受众地区',
            '可选主题': ['现代言情', '古代言情', '狼人'],
            '可选地区': ['欧美', '东南亚', '中日韩'],
            '输出规范': {
                '输出格式': 'json',
                '输出限制': '主题的可选取值参见[可选主题], 受众地区的可选取值参见[可选地区], '
                '输出不允许超出已知取值范围.',
                '输出示例': {
                    'chain_of_thought': '<在这里给出你的思考过程, 4000字>',
                    'output': '主题为: ..., 受众地区: ...'
                }
            },
            '输出开始': '你的输出以 "主题为: " 正式开始.'
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
