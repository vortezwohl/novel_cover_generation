from covgen.api import simple_cover_gen
from covgen.data import CoverGenReq

if __name__ == '__main__':
    images = simple_cover_gen(CoverGenReq(
        novel='The Secret I Heard\nIn New York',
        title='The Secret I Heard\nIn New York',
        title_height_correction=-384))['b64_images']
    for i, img in enumerate(images):
        img.save(rf'D:\project\covgen\test\output\cover_imitation_simple_{i}.png')
