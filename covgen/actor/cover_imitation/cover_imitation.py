import json

from covgen.actor import ark_image_model, ark_client
from covgen.actor.image_understanding.image_understanding import ImageUnderstanding


class CoverImitation(object):
    def __init__(self, title: str, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt: dict = dict({'图片风格为': '', '图片用途': ''})
        self._prompt.update(ImageUnderstanding(
            base64_image=base64_image,
            image_format=image_format
        ).image_features().get('output'))
        if self._prompt is not None:
            self._prompt['图片风格为'] = self._prompt['呈现类型']
            del self._prompt['呈现类型']
            self._prompt['文案内容']['书名'] = title
        self._prompt = f'请参考图片描述: {json.dumps(self._prompt, ensure_ascii=False)}. 生成一份带有书名的书封图, 书名为《{title}》'

    def generate(self, size: str = '720x960') -> str:
        resp = ark_client.images.generate(
            model=ark_image_model,
            prompt=self._prompt,
            size=size,
            response_format='url',
            watermark=False
        )
        return resp.data[0].url


if __name__ == '__main__':
    from covgen.util.image_stringifier import stringify
    print(CoverImitation('六百六十六', stringify(r'D:\project\covgen\resource\knowledge_base\female_oriented\ancient_romance\eastasia_anime\2.png'), 'png').generate())
