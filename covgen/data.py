import dataclasses

from pydantic import BaseModel

from covgen.util.image_stringifier import image_to_base64
from covgen.util.read_file import get_files
from resource import COMMON_ROOT


@dataclasses.dataclass
class CoverGenReq(BaseModel):
    novel: str
    title: str
    title_color: list = None
    title_height_correction: float = .0
    resample: int = 1


@dataclasses.dataclass
class CoverGenResp:
    def __init__(self, b64_image: list[str | None]):
        self.b64_image = b64_image

    def to_dict(self):
        return {'b64_images': [x if x is not None else image_to_base64(get_files(COMMON_ROOT)[0], image_format='png')
                               for x in self.b64_image]}


@dataclasses.dataclass
class TitledCoverGenReq(BaseModel):
    novel: str
    title: str
    resample: int = 1
