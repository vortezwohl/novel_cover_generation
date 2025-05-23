import logging

from covgen.actor import ark_image_model, ark_language_model, ark_client
from covgen.actor.image_understanding.image_understanding import ImageUnderstanding

log = logging.getLogger('covgen')


class CoverImitation(object):
    def __init__(self, title: str, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstanding(
            base64_image=base64_image,
            image_format=image_format
        ).image_features()
        self._prompt = (f'### 重要信息\n- 书名为: {title}'
                        '\n- 文字展示要求: 图中仅展示书名, 且无任何其他文字'
                        '\n- 视角: 正面') + ark_client.chat.completions.create(
            model=ark_language_model,
            messages=[
                {
                    'role': 'system',
                    'content': [
                        {
                            'type': 'text',
                            'text': '你是一个提示词撰写专家, 将这段用于生成正面书封的以 Json 为主的[原始提示词]改写为**可读性更优**'
                                    '且**十分简短(199字)**的 Markdown 格式提示词, 用于文生图任务. '
                                    '提示词需要分为两大块, 一块是"书名信息", 一块是"视觉元素". 你的输出以 "## 书名信息\n" 开始.'
                        }
                    ]
                },
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': f'[原始提示词]: "请为《{title}》生成一份适合网文的平面书封 (必须在书封中写上书名) , 书封图片描述: {self._prompt}".'
                        }
                ]
            }],
            temperature=0.05,
            top_p=0.1
        ).choices[0].message.content
        log.debug(f'cover_imitation_prompt: {self._prompt}')

    def generate(self, size: str = '720x960') -> str:
        resp = ark_client.images.generate(
            model=ark_image_model,
            prompt=self._prompt,
            size=size,
            response_format='url',
            watermark=False,
            guidance_scale=4
        )
        return resp.data[0].url


if __name__ == '__main__':
    from covgen.util.image_stringifier import stringify
    print(CoverImitation('六百六十六', stringify(r'D:\project\covgen\resource\knowledge_base\female_oriented\ancient_romance\eastasia_anime\1.png'), 'png').generate())
