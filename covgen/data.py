import dataclasses

from pydantic import BaseModel


@dataclasses.dataclass
class CoverGenReq(BaseModel):
    novel: str
    title: str
    title_color: list = None
    title_height_correction: float = .0
    resample: int = 1


@dataclasses.dataclass
class CoverGenResp:
    def __init__(self, b64_image: list[str]):
        self.b64_image = b64_image

    def to_dict(self):
        return {'b64_images': self.b64_image}


@dataclasses.dataclass
class TitledCoverGenReq(BaseModel):
    novel: str
    title: str
    resample: int = 1
