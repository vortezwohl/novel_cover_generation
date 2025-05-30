import logging
import os.path
from concurrent.futures import ThreadPoolExecutor
from random import choice

from resource import FEMALE_ORIENTED_KB_ROOT, EN_FONT_ROOT, ZH_FONT_ROOT
from covgen.enum.lang import Lang
from covgen.util.image_stringifier import image_to_base64
from covgen.util.read_file import get_files
from covgen.data import CoverGenReq, CoverGenResp, TitledCoverGenReq
from covgen.enum.region import Region
from covgen.enum.subject import Subject
from covgen.actor.cover_imitation.cover_imitation import CoverImitation
from covgen.actor.title_generation.simple_title_generation import SimpleTitleGeneration
from covgen.actor.title_generation.diffuser_titled_cover_generation import DiffuserTitledCoverGeneration
from covgen.actor.novel_theme_recognition.novel_theme_recognition import NovelThemeRecognition
from covgen.actor.novel_language_recognition.novel_language_recognition import NovelLanguageRecognition

log = logging.getLogger('covgen')


def __choose_title_font(title: str, novel: str):
    font_root = None
    lang = NovelLanguageRecognition(title=title, novel=novel).recognize()
    match lang:
        case Lang.Zh:
            font_root = ZH_FONT_ROOT
        case Lang.En:
            font_root = EN_FONT_ROOT
    font = choice(get_files(font_root))
    log.debug(f'font: {font}')
    return font


def simple_cover_gen(req: CoverGenReq) -> dict:
    def from_b64_image_to_cover(b64_image: str) -> str:
        nonlocal req
        return SimpleTitleGeneration(
            title=req.title, base64_image=CoverImitation(base64_image=b64_image, image_format='png').generate(),
            title_color=tuple(req.title_color), title_font=__choose_title_font(req.title, req.novel),
            title_height_correction=req.title_height_correction
        ).generate()

    novel_content = f'《{req.title}》\n{req.novel}'
    subject, region = NovelThemeRecognition(novel=novel_content).recognize()
    subject_path = region_path = None
    match subject:
        case Subject.ModernRomance:
            subject_path = 'modern_romance'
            match region:
                case Region.Western:
                    region_path = 'western_realistic'
                case Region.SouthEastAsia:
                    region_path = 'southeastasia_realistic'
                case Region.EastAsia:
                    region_path = 'eastasia_anime'
        case Subject.AncientRomance:
            subject_path = 'ancient_romance'
            region_path = 'eastasia_anime'
        case Subject.Werewolves:
            subject_path = 'werewolves'
            region_path = choice(['western_anime', 'western_realistic'])
    if subject_path is None or region_path is None:
        subject_path = 'modern_romance'
        region_path = 'western_realistic'
    kb_path = os.path.join(FEMALE_ORIENTED_KB_ROOT, subject_path, region_path)
    kb_images = get_files(kb_path)
    the_rand_kb_image = [choice(kb_images) for _ in range(req.resample)]
    b64_images = [image_to_base64(uri=x, image_format='png') for x in the_rand_kb_image]
    b64_new_images_with_title = []
    with ThreadPoolExecutor(max_workers=min(req.resample, 16)) as executor:
        b64_new_images_with_title = list(executor.map(from_b64_image_to_cover, b64_images))
    return CoverGenResp(b64_image=b64_new_images_with_title).to_dict()


def diffuser_titled_cover_gen(req: TitledCoverGenReq):
    def from_b64_image_to_titled_cover(b64_image: str) -> str:
        nonlocal req
        return DiffuserTitledCoverGeneration(
            title=req.title,
            base64_image=CoverImitation(base64_image=b64_image, image_format='png').generate(),
            image_format='png'
        ).generate()

    novel_content = f'《{req.title}》\n{req.novel}'
    subject, region = NovelThemeRecognition(novel=novel_content).recognize()
    subject_path = region_path = None
    match subject:
        case Subject.ModernRomance:
            subject_path = 'modern_romance'
            match region:
                case Region.Western:
                    region_path = 'western_realistic'
                case Region.SouthEastAsia:
                    region_path = 'southeastasia_realistic'
                case Region.EastAsia:
                    region_path = 'eastasia_anime'
        case Subject.AncientRomance:
            subject_path = 'ancient_romance'
            region_path = 'eastasia_anime'
        case Subject.Werewolves:
            subject_path = 'werewolves'
            region_path = choice(['western_anime', 'western_realistic'])
    if subject_path is None or region_path is None:
        subject_path = 'modern_romance'
        region_path = 'western_realistic'
    kb_path = os.path.join(FEMALE_ORIENTED_KB_ROOT, subject_path, region_path)
    kb_images = get_files(kb_path)
    the_rand_kb_image = [choice(kb_images) for _ in range(req.resample)]
    b64_images = [image_to_base64(uri=x, image_format='png') for x in the_rand_kb_image]
    b64_new_images_with_title = []
    with ThreadPoolExecutor(max_workers=min(req.resample, 16)) as executor:
        b64_new_images_with_title = list(executor.map(from_b64_image_to_titled_cover, b64_images))
    return CoverGenResp(b64_image=b64_new_images_with_title).to_dict()
