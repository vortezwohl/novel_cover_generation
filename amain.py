import base64
import logging
import os
from io import BytesIO

from PIL import Image
from async_service import AsyncService

from cdLogger import configure_logging
from config import AppConfig, SettingKey
from covgen.api import simple_cover_gen, diffuser_titled_cover_gen
from covgen.data import CoverGenReq, TitledCoverGenReq

client = AppConfig()
configure_logging(client.get_value(SettingKey.Kafka_HOST.value), client.get_value(SettingKey.Kafka_TOPIC.value))
logging.getLogger('volcenginesdkarkruntime').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)
logging.getLogger('python_apollo_client').setLevel(logging.ERROR)
logger = logging.getLogger('ENTRY_POINT')


def covgen_service(task_type: str, **kwargs) -> dict:
    novel = kwargs['novel']
    title = kwargs['title']
    resample = 1
    target_file_path = kwargs['target_file_url']
    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
    b64_images_gen = None
    match task_type:
        case 'simple':
            title_color = kwargs.get('title_color', None)
            title_height_correction = kwargs.get('title_height_correction', .0)
            req = CoverGenReq(novel=novel, title=title, title_color=title_color,
                              title_height_correction=title_height_correction, resample=resample)
            b64_images_gen = simple_cover_gen(req)['b64_images'][0]
        case 'diffuser':
            req = TitledCoverGenReq(novel=novel, title=title, resample=resample)
            b64_images_gen = diffuser_titled_cover_gen(req)['b64_images'][0]
        case _: ...
    if b64_images_gen:
        stream = BytesIO(base64.b64decode(b64_images_gen))
        Image.open(stream).save(target_file_path, format='PNG')
        return {'result': 'success', 'path': target_file_path}
    return {'result': 'failure', 'path': ''}


if __name__ == '__main__':
    AsyncService(covgen_service, service_key=25, service_name='CovGen',
                 listeners=256, use_larger_data=False, expected_time_per_request=300,
                 logger=logger, verbose=False, history_daemon=True).serve()
