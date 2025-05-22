import json

from covgen.actor import ark_image_model, ark_client
from covgen.actor.image_understanding.image_understanding import ImageUnderstanding


class CoverImitation(object):
    def __init__(self, title: str, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstanding(base64_image=base64_image, image_format=image_format).image_features().get('output')
        if self._prompt is not None:
            del self._prompt['文案内容']['作者']
            self._prompt['文案内容']['书名'] = title

    def generate(self, size: str = '720x960') -> list[str]:
        resp = ark_client.images.generate(
            model=ark_image_model,
            prompt=json.dumps(self._prompt, ensure_ascii=False),
            size=size,
            response_format='url',
            watermark=False
        )
        return resp.data[0].url


if __name__ == '__main__':
    from covgen.util.image_stringifier import stringify
    print(CoverImitation('我是吴子豪', stringify(r'D:\project\covgen\resource\knowledge_base\female_oriented\ancient_romance\eastasia_anime\3.png'), 'png').generate())
