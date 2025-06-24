import json
import logging
import random

from covgen.util.hash import md5
from covgen.actor import ark_language_model, ark_client
from covgen.actor.image_understanding.image_understanding_prompt import ImageUnderstandingPrompt

log = logging.getLogger('covgen')
CACHE = dict()
DEFAULT_DESCR = '''
{呈现类型: 欧美真人; 人物形象与性别: 包含一男一女两位人物;
人物神态(眼神、动作、表情、心情): 眼神闭合或低垂，男性拥靠、女性依偎的亲密动作，表情温柔放松，传递亲昵、依恋的心情;
人物年龄: 青年（约20 - 30岁）;  人物外貌: 女性卷发、精致妆容、佩戴项链与耳环；男性发型整齐、身着白衬衫与深色西装、面部轮廓立体;
人物种族/地域特征: 具有欧美地域特征;  人物的其他补充信息: 人物服饰精致，女性有配饰点缀，男性着正式西装，强化角色气质;
图像氛围: 浪漫、亲密且带有复古奢华感;
图像情绪: 深情、温柔、依恋;  
图像构图特点: {
主体构图: 两位人物紧密依偎占据画面中心，通过肢体互动强化情感表达，形成视觉焦点;
背景构图: 以简化室内元素（如画框）为主，光影柔和且相对虚化，突出人物同时增添复古层次感},
色彩特点: 暖色调为主，色彩层次丰富，光影过渡自然，具油画质感，通过色彩冷暖对比与光影塑造增强立体感与情感氛围;
风格特点: 精致写实的商业插画风格，聚焦浪漫爱情题材，注重情感传递与氛围营造，细节处理细腻，契合言情类书籍封面视觉需求}
'''


class ImageUnderstanding(object):
    def __init__(self, base64_image: str, image_format: str):
        self._base64_image = base64_image
        self._image_format = image_format
        self._prompt = ImageUnderstandingPrompt(base64_image=base64_image, image_format=image_format)
        self._msg_hash = md5(json.dumps(self._prompt.message_with_image))

    def image_features(self) -> str:
        if self._msg_hash in CACHE.keys() and random.uniform(0, 1) > .33:
            decr = CACHE[self._msg_hash]
            log.debug(f'image_understanding_cache: {decr}')
            return decr
        try:
            decr = ark_client.chat.completions.create(
                model=ark_language_model,
                messages=self._prompt.message_with_image,
                temperature=0.2,
                top_p=0.3
            ).choices[0].message.content
            decr = json.loads(decr).get('output')
            log.debug(f'image_understanding: {decr}')
            CACHE[self._msg_hash] = decr
            return decr
        except json.decoder.JSONDecodeError as e:
            log.error(e)
            return DEFAULT_DESCR
