from covgen.common.base_prompt import BasePrompt


class ImageUnderstandingPrompt(BasePrompt):
    def __init__(self, base64_image: str, image_format: str):
        super().__init__()
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = {
            '你是': '一个擅长平面设计与绘画的商业艺术家',
            '目标': '严格遵循以下[任务步骤], 逐步完成任务, 并根据[输出规范]产生输出.',
            '任务背景': '在你面前的是一份图像, 这份图像被用作一本书的封面, 你需要对这份图像进行解构与学习.',
            '任务步骤': {
                '图像解构': {
                    'step_1': '分析图像的呈现类型, 是写实还是立绘',
                    'step_2': '分析[图像]中的人物形象, 人物外貌, 种族/地域特征等(尽可能全面)',
                    'step_3': '分析[图像]中的氛围与情绪渲染',
                    'step_4': '分析[图像]的构图特点, 包括主体构图, 背景构图与文案构图',
                    'step_5': '分析[图像]的色彩与风格特点'
                },
                '文案提取': {
                    'step_1': '认真观察[图像], 在[图像]中找出[文案](即文本内容), 并在[文案]中找出[书名][作者][其他修饰性文字][其他功能性文字].',
                    'step_2': '详细解析[文案]的布局与字体风格(可能存在多种字体风格), 请特别关注文案布局与图像主体的关系与照应.'
                }
            },
            '输出规范': {
                '输出格式': 'json',
                '输出框架': {
                    'chain_of_thought': '<在这里给出你的思考过程, 4000字>',
                    'output': {
                        '呈现类型': '...',
                        '人物形象': '...',
                        '人物外貌': '...',
                        '人物种族/地域特征': '...',
                        '人物的其他补充信息': '...',
                        '图像氛围': '...',
                        '图像情绪': '...',
                        '图像构图特点': {
                            '主体构图': '...',
                            '背景构图': '...',
                            '文案构图': '...'
                        },
                        '色彩特点': '...',
                        '风格特点': '...',
                        '文案内容': {
                            '作者': '...',
                            '书名': '...',
                            '其他修饰性文字描述': '...',
                            '其他功能性文字描述': '...'
                        },
                        '文案布局描述': '...',
                        '字体风格描述': '...'
                    }
                }
            },
            '输出开始': '你的输出以 \"{"chain_of_thought":\"开始.'
        }

    @property
    def message_with_image(self) -> list:
        return [{
            'role': 'user',
            'content': [
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/{self._image_format};base64,{self._base64_image}'
                    }
                },
                {
                    'type': 'text',
                    'text': self.prompt
                }
            ]
        }]
