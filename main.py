import base64
import logging
from io import BytesIO
import tempfile

from PIL import Image
from fastapi import FastAPI
from starlette.responses import StreamingResponse

from cdLogger import configure_logging
from config import SettingKey, AppConfig
from covgen.api import simple_cover_gen, CoverGenReq

client = AppConfig()
configure_logging(client.get_value(SettingKey.Kafka_HOST.value), client.get_value(SettingKey.Kafka_TOPIC.value))
logger = logging.getLogger(__name__)
app = FastAPI()


@app.get('/gen/simple')
async def simple_cover_generation(req: CoverGenReq):
    logger.debug(req)
    req.resample = 1
    stream = BytesIO(base64.b64decode(simple_cover_gen(req)['b64_images'][0]))
    image_file = Image.open(stream)
    temp_file = tempfile.NamedTemporaryFile(delete_on_close=True, suffix='.png')
    image_file.save(temp_file, format='PNG')
    temp_file.seek(0)
    return StreamingResponse(temp_file,
                             media_type='image/png',
                             headers={"Content-Disposition": "attachment; filename=image.png"})
