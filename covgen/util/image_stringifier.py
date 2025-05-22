import base64
import requests


def stringify(uri: str) -> str:
    decoding = 'utf-8'
    if uri.startswith('ht'):
        return base64.b64encode(requests.get(url=uri).content).decode(decoding)
    else:
        with open(uri, mode='rb') as f:
            return base64.b64encode(f.read()).decode(decoding)
