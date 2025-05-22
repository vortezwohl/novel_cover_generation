import json

from covgen.actor import ark_model, ark_client
from covgen.actor.image_understanding.image_understanding_prompt import ImageUnderstandingPrompt


class ImageUnderstanding(object):
    def __init__(self, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstandingPrompt(base64_image=base64_image, image_format=image_format)

    def image_features(self, max_retries: int = 5) -> dict | None:
        _retries = 0
        outer_keys = ['chain_of_thought', 'output']
        keys = ['呈现类型', '人物形象',
                '人物外貌', '人物种族/地域特征',
                '人物的其他补充信息', '图像氛围',
                '图像情绪', '图像构图特点',
                '色彩特点', '风格特点',
                '文案内容', '文案布局描述',
                '字体风格描述']
        sub_keys_0 = ['主体构图', '背景构图', '文案构图']
        sub_keys_1 = ['作者', '书名', '其他修饰性文字描述', '其他功能性文字描述']
        while True:
            if _retries >= max_retries:
                return None
            try:
                resp = ark_client.chat.completions.create(
                    model=ark_model,
                    messages=self._prompt.message_with_image
                ).choices[0].message.content
                resp_dict = json.loads(resp)
                for o_k in outer_keys:
                    if o_k not in resp_dict.keys():
                        continue
                output_dict = resp_dict[outer_keys[1]]
                for k in keys:
                    if k not in output_dict.keys():
                        continue
                if '图像构图特点' in output_dict.keys():
                    if isinstance(output_dict['图像构图特点'], dict):
                        for s_k in sub_keys_0:
                            if s_k not in output_dict['图像构图特点'].keys():
                                continue
                    else:
                        continue
                if '文案内容' in output_dict.keys():
                    if isinstance(output_dict['文案内容'], dict):
                        for s_k in sub_keys_1:
                            if s_k not in output_dict['文案内容'].keys():
                                continue
                    else:
                        continue
                return resp_dict
            except json.decoder.JSONDecodeError:
                continue
            finally:
                _retries += 1


if __name__ == '__main__':
    from covgen.util.image_stringifier import stringify
    image_understanding = ImageUnderstanding(
        stringify(r'D:\project\covgen\resource\knowledge_base\female_oriented\ancient_romance\eastasia_anime\1.png'),
        image_format='png'
    )
    print(image_understanding.image_features())
