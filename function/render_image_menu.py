from PIL import Image, ImageFilter
import pytesseract


def render():
    img = Image.open("../menu/menu_today.jpg")

    pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
    config_for_dish = '--oem 3 --psm 6 -l rus --tessdata-dir "C:/Program Files/Tesseract-OCR"'

    menu = ['Закуски', 'Салаты', 'Супы', 'Блюда', 'Гарниры', 'Десерты', 'Напитки', 'Кулинарные', 'Хлебобулочные',
            'Начальник']

    dishes_img = img.crop((50, 80, 430, img.size[1]))

    res = []
    k = 0
    photo = [dishes_img, dishes_img.filter(ImageFilter.SHARPEN)]

    while len(res) not in (9, 10):
        data = pytesseract.image_to_data(photo[k], config=config_for_dish)

        res = []
        for i, el in enumerate(data.splitlines()):
            if i == 0:
                continue

            el = el.split()
            try:

                if el[-1].capitalize().replace('.', '') in menu:
                    x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])
                    res.append([x, y, w, el[-1].capitalize().replace('.', '')])
                elif el[-1].capitalize().replace('.', '') in ['Издел', 'Цоп']:
                    x, y, w, h = int(el[6]), int(el[7]), int(el[8]), int(el[9])
                    res.append([x, y, w, el[-1].capitalize().replace('.', '')])
            except IndexError:
                pass
        k += 1

    print(res)
    # 700 650

    menu_name = ["Холодные закуски", "Салаты", "Супы", "Горячие блюда", "Гарниры", "Десерты", "Напитки",
                 "Хлеб и хлебобулочные изделия"]

    if len(res) == 10:
        menu_name.insert(-1, "Мучные и кулинарные изделия")

    dishes_img_new = img.crop((50, 80, 730, res[-1][1] + 82)).filter(ImageFilter.SHARPEN)

    dishes_img_new.save('../menu/Меню целиком.jpg')

    for i, v in enumerate(res[:-1]):

        if res[i] == res[-1]:
            dish_img = dishes_img_new.crop((0, v[1] - 5, 680, dishes_img_new.size[1]))
        else:
            dish_img = dishes_img_new.crop((0, v[1] - 5, 680, res[i + 1][1]))

        dish_img.save(f"../menu/{menu_name[i]}.jpg")
