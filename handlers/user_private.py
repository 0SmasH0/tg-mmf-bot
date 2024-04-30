import json
import datetime

from aiogram import types, Router, F, Bot

from aiogram.filters import Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic, Text

from keyboards import reply
from filters.chat_types import ChatTypeFilter
from keyboards import dynamic_kb
from dotenv import find_dotenv, load_dotenv
from function.text_refactor import refactoring_text, full_decor, section_decor

from keyboards.dynamic_kb import dynamics_kb_subgroups, dynamics_kb_menu, dynamics_kb_groups

load_dotenv(find_dotenv())

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(Command('start'))
async def start_cmd(message: types.Message, state: FSMContext):
    text = as_list(Bold("Добро пожаловать в MMF Helper!"), "\nВыберите интересующий вас пункт")
    current_state = await state.get_state()
    if current_state:
        await state.clear()
    await message.answer(text.as_html(), reply_markup=reply.start_kb.as_markup(resize_keyboard=True))


@user_private_router.message(F.text.lower().contains('в начало'))
async def start(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()

    text = Bold('Выберите интересующий вас пункт')

    await message.answer(text.as_html(), reply_markup=reply.start_kb.as_markup(resize_keyboard=True))


@user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer('Здесь пока ничего нет', reply_markup=reply.back_to_start.as_markup(resize_keyboard=True))


# Код ниже состояния диалога по кнопке "Меню столовой"

class KitchenMenu(StatesGroup):
    text = State()


@user_private_router.message(StateFilter(None), F.text.lower().contains("меню столовой"))
async def kitchen_menu(message: types.Message, state: FSMContext):
    preview = Bold('Выберите интересующую вас позицию меню')
    kb_m = dynamics_kb_menu()
    await message.answer(preview.as_html(), reply_markup=kb_m.as_markup(resize_keyboard=True))
    await state.set_state(KitchenMenu.text)


@user_private_router.message(KitchenMenu.text, F.text)
async def kitchen_menu_2(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()

    menu = ['Меню целиком', 'Горячие блюда', 'Гарниры', 'Супы', 'Салаты', 'Десерты', 'Напитки',
            'Холодные закуски', 'Хлеб и хлебобулочные изделия', "Мучные и кулинарные изделия"]

    for i in range(len(menu)):
        file_path = fr"menu\{menu[i]}.jpg"

        if data['text'] == menu[i]:

            await message.answer_photo(photo=types.FSInputFile(path=file_path))

        elif data['text'][:-1] == menu[i]:

            await message.answer_photo(photo=types.FSInputFile(path=file_path))


class Schedule(StatesGroup):
    course = State()
    group = State()
    subgroup = State()
    choice = State()

    texts = {
        'Schedule:course': 'Выберите курс заново',
        'Schedule:group': 'Выберите группу заново',
        'Schedule:subgroup': 'Выберите подгруппу заново',
    }


#Вернутся на шаг назад (на прошлое состояние)
@user_private_router.message(StateFilter('*'), F.text.lower().contains("вернуться назад"))
async def back_step_handler(message: types.Message, state: FSMContext) -> Message | None:
    current_state = await state.get_state()

    previous = None

    for step in Schedule.__all_states__:
        if step.state == current_state:
            info = f"Вы вернулись к прошлому шагу \n\n<b>{Schedule.texts[previous.state]}</b>"
            await state.set_state(previous)

            match previous.state:
                case Schedule.course:
                    await message.answer(f'{info}', reply_markup=reply.courses.as_markup(resize_keyboard=True))

                case Schedule.group:
                    data = await state.get_data()
                    course_now = data['course']
                    kb = dynamic_kb.dynamics_kb_groups(course_now)
                    await state.update_data(subgroup=[])
                    await message.answer(f'{info}', reply_markup=kb.as_markup(resize_keyboard=True))

                case Schedule.subgroup:
                    data = await state.get_data()
                    kb_s = dynamics_kb_subgroups(data['course'], data['group'])[0]

                    if kb_s is None:
                        await state.set_state(Schedule.group)
                        course_now = data['course']
                        await state.update_data(subgroup=[])
                        kb = dynamic_kb.dynamics_kb_groups(course_now)
                        info = f"Вы вернулись к прошлому шагу \n\n<b>{Schedule.texts["Schedule:subgroup"]}</b>"
                        await message.answer(f'{info}', reply_markup=kb.as_markup(resize_keyboard=True))
                        return

                    await state.update_data(subgroup=[])
                    await message.answer(f'{info}', reply_markup=kb_s.as_markup(resize_keyboard=True))

            return
        previous = step


@user_private_router.message(StateFilter(None), F.text.lower().contains("расписание занятий"))
async def schedule_1(message: types.Message, state: FSMContext):
    text = Bold('Выберите курс')
    await message.answer(text.as_html(), reply_markup=reply.courses.as_markup(resize_keyboard=True))
    await state.set_state(Schedule.course)


@user_private_router.message(Schedule.course, F.text)
async def schedule_2(message: types.Message, state: FSMContext):
    if message.text.isdigit() and 1 <= int(message.text) <= 4:
        await state.update_data(course=message.text)
        data = await state.get_data()

        course_now = data['course']
        kb = dynamics_kb_groups(course_now)

        await message.answer(Bold('Выберите группу').as_html(), reply_markup=kb.as_markup(resize_keyboard=True))
        await state.set_state(Schedule.group)
    else:
        await message.answer(f'Нет такого курса 🥲', reply_markup=reply.courses.as_markup(resize_keyboard=True))


@user_private_router.message(Schedule.group, F.text)
async def schedule_3(message: types.Message, state: FSMContext):
    file_path = fr"schedule\data.json"
    with open(file_path, "rb") as foo:
        last = json.load(foo)

    data = await state.get_data()
    var = last.get(data['course'])
    if var is None:
        var = 10

    if message.text == 'ВФ' or (message.text.isdigit() and 1 <= int(message.text) <= int(var)):
        if message.text == 'ВФ':
            await state.update_data(group='vf')
        else:
            await state.update_data(group=message.text)

        data = await state.get_data()
        kb_s = dynamics_kb_subgroups(data['course'], data['group'])[0]

        if kb_s is None:
            await state.update_data(subgroup=[])
            await message.answer(Bold('Выберите подходящий вам пункт').as_html(),
                                 reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))
            await state.set_state(Schedule.choice)
            return

        preview = as_list(
            as_marked_section(
                Bold('Инструкция по использованию:'),
                Italic(f'1️⃣ Чтобы выбрать подгруппу нажмите на соответствущую кнопку в меню.'),
                Italic(f'2️⃣ Чтобы убрать уже выбранную подгруппу нажмите на неё ещё раз.'),
                Italic(f'3️⃣ Чтобы выбрать(убрать) все подгруппы, можно нажать кнопку \"Выбрать всё\".'),
                Italic(f'4️⃣ После того как вы выбрали нужные(-ую) вам подгруппы(-у) нажмите кнопку \"Готово\".\n'),
                marker=''
            ),
            Bold(f'Выберите нужные(-ую) вам подгруппы(-у):'),
        )

        await message.answer(preview.as_html(), reply_markup=kb_s.as_markup(resize_keyboard=True))
        await state.set_state(Schedule.subgroup)
    else:

        kb = dynamic_kb.dynamics_kb_groups(data['course'])

        await message.answer(f'Нет такой группы 🥲', reply_markup=kb.as_markup(resize_keyboard=True))


@user_private_router.message(Schedule.subgroup, F.text)
async def schedule_4(message: types.Message, state: FSMContext):
    data = await state.get_data()

    kb_s, sbg = dynamics_kb_subgroups(data['course'], data['group'])

    if 'subgroup' not in data:
        data.update({'subgroup': []})

    if message.text not in [*sbg, 'Готово', 'Выбрать всё']:
        await message.answer(f'Нет такой подгруппы 🥲',
                             reply_markup=kb_s.as_markup(resize_keyboard=True))
        return

    elif message.text == "Готово":
        await state.set_state(Schedule.choice)
        await state.update_data(subgroup=data['subgroup'])
        await message.answer(Bold('Выберите подходящий вам пункт').as_html(),
                             reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))
        return

    elif message.text == 'Выбрать всё':
        if len(data['subgroup']) == len(sbg):
            data['subgroup'] = []
        else:
            data['subgroup'] = sbg

    elif message.text not in data['subgroup']:
        data['subgroup'].append(message.text)

    else:
        data['subgroup'].remove(message.text)

    await state.update_data(subgroup=data['subgroup'])

    if not data['subgroup']:
        await message.answer(f"{f'<i>У вас ничего не выбрано</i>'}",
                             reply_markup=kb_s.as_markup(resize_keyboard=True))
    else:
        await message.answer(f"{f'<i>У вас выбрано:</i> <b>{", ".join(sorted(data["subgroup"]))}</b>'}",
                             reply_markup=kb_s.as_markup(resize_keyboard=True))


@user_private_router.message(Schedule.choice, F.text)
async def schedule_5(message: types.Message, state: FSMContext):
    await state.update_data(choice=message.text)
    data = await state.get_data()

    date = datetime.datetime.now()

    k = data['course']
    g = data['group']

    if g.isdigit():
        file_path = fr"schedule\{k}-kurs\{k}-{g}.json"

    else:
        file_path = fr"schedule\{k}-kurs\{k}-vf.json"

    with open(file_path, 'rb') as file:
        sc = json.load(file)

    with open('week_today.txt', 'r', encoding='utf-8') as foo:
        week = foo.read()

    sbg = data['subgroup']
    sbg.extend([week])

    day_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    sub = {"time": 'Время', "remarks": 'Группа', "subject": 'Предмет', "lecture-practice": 'Тип',
           "room": 'Кабинет', "teacher": 'Преподаватель', "date": 'Дни проведения'}

    if data['choice'] == 'На сегодня':
        day = date.weekday()
        info = sc[day_of_week[day]] if (day_of_week[day] in sc) else False

        if not info:
            await message.answer('У вас нет сегодня пар!!!',
                                 reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))
            return
        else:
            my_list_2 = refactoring_text(info, sbg, date, sub)

            if not my_list_2:
                await message.answer('У вас нет сегодня пар!!!',
                                     reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))

            else:
                formatted_date = date.strftime("%d.%m.%Y")
                texts = full_decor(section_decor(my_list_2, day_of_week[day], formatted_date), data['choice'].lower(),
                                   k, g)

                await message.answer(texts.as_html(), reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))

    elif data['choice'] == 'На завтра':
        day = date + datetime.timedelta(days=1)
        d_t = day.weekday()
        info = sc[day_of_week[d_t]] if (day_of_week[d_t] in sc) else False
        if not info:
            await message.answer('У вас нет завтра пар!!!',
                                 reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))
            return
        else:
            my_list_2 = refactoring_text(info, sbg, day, sub)
            if not my_list_2:
                await message.answer('У вас нет завтра пар!!!',
                                     reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))

            else:
                formatted_date = day.strftime("%d.%m.%Y")
                texts = full_decor(section_decor(my_list_2, day_of_week[d_t], formatted_date), data['choice'].lower(),
                                   k, g)
                await message.answer(texts.as_html(), reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))

    elif data['choice'] == 'На неделю':
        if sc == {}:
            await message.answer("Вообще нету пар!!!", reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))
        else:
            full_res = []
            for v in sc:
                idx = day_of_week.index(v)
                day = date.weekday()
                dif = idx - day
                if day in (5, 6):
                    res = date + datetime.timedelta(days=dif) + datetime.timedelta(days=7)
                else:
                    res = date + datetime.timedelta(days=dif)

                my_list_2 = refactoring_text(sc[v], sbg, res, sub)

                if my_list_2:
                    formatted_date = res.strftime("%d.%m.%Y")
                    schedule = section_decor(my_list_2, v, formatted_date)
                    full_res.append(schedule)

            if full_res:
                texts = full_decor(full_res, data['choice'].lower(), k, g)
                if len(texts) > 4096:
                    for x in range(0, len(texts), 4096):
                        await message.answer(texts[x:x + 4096].as_html(),
                                             reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))
                else:
                    await message.answer(texts.as_html(), reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))
            else:
                await message.answer('У вас нет пар!!!',
                                     reply_markup=reply.choice_sc.as_markup(resize_keyboard=True))

    else:
        await message.answer('Нет такого пункта 🥲')


@user_private_router.message(F.text)
async def cmd(message: types.Message):
    await message.answer('Пожалуйста, выберите корректную кнопку')


@user_private_router.message(F.text.lower() == 'прочее')
async def cmd(message: types.Message):
    await message.answer('Пожалуйста, выберите корректную кнопку')
