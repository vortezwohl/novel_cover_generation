from covgen.actor.image_understanding.image_understanding import ImageUnderstanding

if __name__ == '__main__':
    from covgen.util.image_stringifier import stringify
    image_understanding = ImageUnderstanding(
        stringify(r'D:\project\covgen\resource\knowledge_base\female_oriented\ancient_romance\eastasia_anime\1.png'),
        image_format='png'
    )
    print(image_understanding.image_features())
