import os.path
from concurrent.futures import ThreadPoolExecutor
from random import choice

from resource import FEMALE_ORIENTED_KB_ROOT, EN_FONT_ROOT, ZH_FONT_ROOT
from covgen.util.image_stringifier import image_to_base64
from covgen.util.read_file import get_files
from covgen.data import CoverGenReq, CoverGenResp
from covgen.enum.region import Region
from covgen.enum.subject import Subject
from covgen.actor.cover_imitation.cover_imitation import CoverImitation
from covgen.actor.title_generation.simple_title_generation import SimpleTitleGeneration
from covgen.actor.novel_theme_recognition.novel_theme_recognition import NovelThemeRecognition


def simple_cover_gen(req: CoverGenReq) -> dict:
    def from_b64_image_to_cover(b64_image: str) -> str:
        nonlocal req
        return SimpleTitleGeneration(
            title=req.title, base64_image=CoverImitation(base64_image=b64_image, image_format='png').generate(),
            title_color=req.title_color, title_font=req.title_font,
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


if __name__ == '__main__':
    images = simple_cover_gen(CoverGenReq(
        novel='The Secret I Heard',
        title='The Secret I Heard',
        title_color=(255, 255, 255),
        title_font=r'D:\project\covgen\resource\font\Aston Script.ttf',
        title_height_correction=-384))['b64_images']
    for i, img in enumerate(images):
        img.save(rf'D:\project\covgen\test\output\cover_imitation_simple_{i}.png')
