import base64
import logging
from io import BytesIO
import tempfile

from PIL import Image
from fastapi import FastAPI
from starlette.responses import StreamingResponse

from cdLogger import configure_logging
from config import SettingKey, AppConfig
from covgen.api import simple_cover_gen, diffuser_titled_cover_gen, CoverGenReq, TitledCoverGenReq

client = AppConfig()
configure_logging(client.get_value(SettingKey.Kafka_HOST.value), client.get_value(SettingKey.Kafka_TOPIC.value))
logging.getLogger('volcenginesdkarkruntime').setLevel(logging.ERROR)
logging.getLogger('httpcore').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)
logging.getLogger('python_apollo_client').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
app = FastAPI()
logger.info('Starting app...')


@app.get('/healthz/ready')
async def health_check():
    return 'OK'


@app.get('/healthz/live')
async def live_check():
    return 'OK'


@app.post('/v1/gen/simple')
async def simple_cover_generation(req: CoverGenReq):
    logger.debug(f'/v1/gen/simple 收到请求: {req}')
    req.resample = 1
    stream = BytesIO(base64.b64decode(simple_cover_gen(req)['b64_images'][0]))
    image_file = Image.open(stream)
    temp_file = tempfile.NamedTemporaryFile(suffix='.png')
    image_file.save(temp_file, format='PNG')
    temp_file.seek(0)
    return StreamingResponse(temp_file,
                             media_type='image/png',
                             headers={"Content-Disposition": "attachment; filename=image.png"})


@app.post('/v1/gen/diffuser')
async def simple_cover_generation(req: TitledCoverGenReq):
    logger.debug(f'/v1/gen/diffuser 收到请求: {req}')
    req.resample = 1
    stream = BytesIO(base64.b64decode(diffuser_titled_cover_gen(req)['b64_images'][0]))
    image_file = Image.open(stream)
    temp_file = tempfile.NamedTemporaryFile(suffix='.png')
    image_file.save(temp_file, format='PNG')
    temp_file.seek(0)
    return StreamingResponse(temp_file,
                             media_type='image/png',
                             headers={"Content-Disposition": "attachment; filename=image.png"})
