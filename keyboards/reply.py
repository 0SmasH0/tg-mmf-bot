from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


back_to_start = ReplyKeyboardBuilder()
back_to_start.add(
    KeyboardButton(text='Вернуться в начало🏠'),
)
back_to_start.adjust(1)


back_btn = ReplyKeyboardBuilder()
back_btn.add(
    KeyboardButton(text='Вернуться назад⬅️'),
)
back_btn.adjust(1)


start_kb = ReplyKeyboardBuilder()
start_kb.add(
    KeyboardButton(text='Расписание занятий👨‍🏫'),
    KeyboardButton(text='Меню столовой🍽️ '),
)
start_kb.adjust(1,1)


courses = ReplyKeyboardBuilder()
courses.add(
    *[KeyboardButton(text=f'{i}') for i in range(1, 5)],
)
courses.attach(back_to_start)
courses.adjust(4)


subgroup = ReplyKeyboardBuilder()
subgroup.add(
    *[KeyboardButton(text=f'{i}') for i in ['a','б','в']],
)
subgroup.attach(back_btn)
subgroup.attach(back_to_start)
subgroup.adjust(3,2)


back_s_b = ReplyKeyboardBuilder()
back_s_b.attach(back_btn)
back_s_b.attach(back_to_start)
back_s_b.adjust(2)

choice_sc = ReplyKeyboardBuilder()
choice_sc.add(
    KeyboardButton(text='На сегодня'),
    KeyboardButton(text='На завтра'),
    KeyboardButton(text='На неделю'),
)
choice_sc.attach(back_btn)
choice_sc.attach(back_to_start)
choice_sc.adjust(2, 1, 2)