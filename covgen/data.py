import dataclasses


@dataclasses.dataclass
class CoverGenReq:
    def __init__(self, novel: str, title: str, title_height_correction: float,
                 title_color: tuple | list = None, resample: int = 4):
        self.novel = novel
        self.title = title
        self.title_color = tuple(title_color) if isinstance(title_color, list) else title_color
        self.title_height_correction = title_height_correction
        self.resample = resample


@dataclasses.dataclass
class CoverGenResp:
    def __init__(self, b64_image: list[str]):
        self.b64_image = b64_image

    def to_dict(self):
        return {'b64_images': self.b64_image}
