import json
import os

from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from keyboards import reply


def dynamics_kb_menu():
    folder_path = fr'menu'
    file_count = sum(len(files[2:]) for _, _, files in os.walk(folder_path))

    list_btn = ['Меню целиком📝', 'Горячие блюда🍖', 'Гарниры🍚', 'Супы🍲',
                'Салаты🥗', 'Десерты🍰', 'Напитки🍵', 'Холодные закуски🦐', 'Хлеб и хлебобулочные изделия🥖',
                "Мучные и кулинарные изделия🥯"]

    kitchen_menu = ReplyKeyboardBuilder()
    kitchen_menu.add(
        *[KeyboardButton(text=f'{list_btn[i]}') for i in range(file_count)]
    )
    kitchen_menu.attach(reply.back_to_start)
    kitchen_menu.adjust(1, 3, 3, 2 if file_count == 9 else 3, 1)
    return kitchen_menu


def dynamics_kb_groups(course):
    file_path = fr"schedule\data.json"
    with open(file_path, "rb") as foo:
        last = json.load(foo)

    for i in last:
        if i.isdigit() and i == course:
            gr = int(last[i])
            groups = ReplyKeyboardBuilder()
            groups.add(
                *[KeyboardButton(text=f'{i}') for i in [*range(1, gr + 1), 'ВФ']]
            )
            groups.attach(reply.back_btn)
            groups.attach(reply.back_to_start)
            groups.adjust(gr - int(gr / 2), int((gr + 1) / 2), 2)
            return groups

    else:
        groups = ReplyKeyboardBuilder()
        groups.add(
            *[KeyboardButton(text=f'{i}') for i in [*range(1, 11), 'ВФ']]
        )
        groups.attach(reply.back_btn)
        groups.attach(reply.back_to_start)
        groups.adjust(6, 5, 2)
        return groups


def dynamics_kb_subgroups(course, group):
    file_path = fr"subgroups.json"
    with open(file_path, "r", encoding='utf-8') as foo:
        sbg = json.load(foo)

    our = sbg[course][group]

    subgroups = ReplyKeyboardBuilder()
    for i in our:
        subgroups.add(
            KeyboardButton(text=f'{i}')
        )

    subgroups.add(
        KeyboardButton(text='Выбрать всё'),
        KeyboardButton(text='Готово')
    )
    subgroups.attach(reply.back_btn)
    subgroups.attach(reply.back_to_start)
    if our:
        subgroups.adjust(len(our), 2, 2)
    else:
        subgroups = None
    return subgroups, our
