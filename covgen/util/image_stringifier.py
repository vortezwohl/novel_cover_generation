import base64
from io import BytesIO
from PIL import Image

import requests


def stringify(uri: str) -> str:
    decoding = 'utf-8'
    if uri.startswith('ht'):
        return base64.b64encode(requests.get(url=uri).content).decode(decoding)
    else:
        with open(uri, mode='rb') as f:
            return base64.b64encode(f.read()).decode(decoding)


def image_to_base64(uri: str, image_format: str) -> str:
    image_data = Image.open(uri)
    buffer = BytesIO()
    image_data.save(buffer, format=image_format)
    image_bytes = buffer.getvalue()
    return base64.b64encode(image_bytes).decode('utf-8')
