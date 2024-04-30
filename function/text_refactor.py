import re
from datetime import datetime

from function.work_with_date import correct_date
from aiogram.utils.formatting import as_list, as_marked_section, Bold, Text


def full_decor(data: Text, choice: str, course: str, group: str) -> Text:
    if group == 'vf' and choice == 'на неделю':
        cor = [*data]
    else:
        cor = [*data] if len([*data]) > 3 else [data]

    group = 'ВФ' if group == 'vf' else group

    text = as_list(
        f"🎓 Расписание {choice} ({course} курс, {group} группа)",
        *cor,
    )
    return text


def section_decor(data: list, day_of_week: str, date: str) -> Text:
    my_dec = as_marked_section(
        Bold(f'\n🗓 {day_of_week}, {date}'),
        *data,
        marker=f'---------------------------------\n'
    )
    return my_dec


def refactoring_text(data: dict, subgroups: list, date: datetime, parameters: dict) -> list:
    list_with_data = []
    for i in data:
        text = ''
        if i['date']:
            many_date = re.findall(r'\([^()]+\)', i['date'])
            if len(many_date) > 1:
                key = 0
                for s in many_date:
                    time = correct_date(s, date)
                    if not (time[0] < date < time[1]):
                        key = 1
                        break
                if key:
                    continue
            else:
                time = correct_date(i['date'], date)
                if not (time[0] < date < time[1]):
                    continue
        if len(i['remarks'].split()) == 1 or i['remarks'] == '':
            if i['remarks'] in subgroups or i['remarks'] == '':
                for k in i:
                    if i[k]:
                        text += f'  {parameters[k]}: {i[k]}\n'
                list_with_data.append(text[:-1])
        else:
            for q in i['remarks'].split():
                if q not in subgroups:
                    break
            else:
                for k in i:
                    if i[k]:
                        text += f'  {parameters[k]}: {i[k]}\n'

                list_with_data.append(text[:-1])

    return list_with_data
