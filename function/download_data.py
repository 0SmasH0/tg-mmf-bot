import json
import os
from datetime import datetime
import re

from bs4 import BeautifulSoup
import http.client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def connect_data():
    host = "mmf.bsu.by"
    conn = http.client.HTTPSConnection(host)
    groups = [*list(range(1, 11)), 'vf']

    return host, conn, groups


def download_menu_food():
    driver = webdriver.Chrome()

    url = 'https://bsu.by/structure/units/tsentr-obshchestvennogo-pitaniya-/menyu'

    driver.get(url)

    wait = WebDriverWait(driver, 15)

    el = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "faculties-page__head")))

    html_content = driver.page_source

    driver.quit()

    soup = BeautifulSoup(html_content, 'html.parser')

    info = soup.find_all('b')[1].get_text().split()[0]
    update_data = {"date": info}

    try:
        with open("../menu/data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        os.mkdir("../menu")
        data = {"date": ""}

    if update_data['date'] > data['date']:
        with open(f"../menu/data.json", "w", encoding='utf-8') as file:
            json.dump(update_data, file, ensure_ascii=False, indent=4)
    else:
        print('У вас актуальное меню')
        return

    img = str(soup.find('img'))
    start, end = img.find('"') + 1, img.rfind('"')

    host = "bsu.by"
    conn = http.client.HTTPSConnection(host)

    photo_url = img[start:end]

    conn.request("GET", photo_url, headers={"Host": host})
    r1 = conn.getresponse()

    with open("../menu/menu_today.jpg", "wb") as file:
        file.write(r1.read())


def download_schedule():
    host, conn, groups = connect_data()

    update_key = 1

    for k in range(1, 5):
        for g in groups:

            if isinstance(g, int):
                url = f'/ru/raspisanie-zanyatij/dnevnoe-otdelenie/{k}-kurs/{g}-gruppa/'
            else:
                url = f'/ru/raspisanie-zanyatij/dnevnoe-otdelenie/{k}-kurs/{g}/'

            conn.request("GET", url, headers={"Host": host})
            r1 = conn.getresponse()

            if r1.status == 200:
                data = r1.read()
            else:
                print(f'Ошибка при скачивании данных. Код ошибки: {r1.status}')
                groups_subgroups = {f"{k}": f"{g - 1}"}
                with open("../schedule/data.json", 'r+') as group:
                    el = json.load(group)
                    el.update(groups_subgroups)
                    group.seek(0)
                    json.dump(el, group, ensure_ascii=False, indent=4)

                conn.close()
                continue

            key_sub = ["weekday", "time", "remarks", "subject", "lecture-practice", "room"]

            soup = BeautifulSoup(data, "html.parser")

            if update_key == 1:
                info = soup.find("caption")
                info_only = info.get_text()
                idx = info_only.rfind('о')
                date_time = info_only[idx + 2:].split(' ')
                update_data = {"date": date_time[0], "time": date_time[1]}

                update_key = 0

                try:
                    with open("../schedule/data.json", "r") as f:
                        data = json.load(f)
                except FileNotFoundError:
                    os.mkdir("../schedule")
                    data = {"date": "", "time": ""}

                if update_data['date'] > data['date']:
                    with open(f"../schedule/data.json", "w", encoding='utf-8') as file:
                        json.dump(update_data, file, ensure_ascii=False, indent=4)
                elif update_data['date'] == data['date']:
                    if update_data['time'] > data['time']:
                        with open(f"../schedule/data.json", "w", encoding='utf-8') as file:
                            json.dump(update_data, file, ensure_ascii=False, indent=4)
                    else:
                        print('У вас актуальные данные')
                        return
                else:
                    print('У вас актуальные данные')
                    return

            table_rows = soup.find_all("tr")  # Найдите все строки таблицы

            # Определите путь к файлу
            file_path = f"../schedule/{k}-kurs/{k}-{g}.json"

            # Создайте каталоги, если они не существуют
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            day_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

            list_json = []
            schedule_json = {}

            with open(file_path, "w", encoding='utf-8') as file:
                for row in table_rows:
                    cells = row.find_all("td")  # все ячейки в строке

                    if len(cells) >= 5:  # Предполагаем, что нужно как минимум пять ячеек

                        if not schedule_json:
                            schedule_json[cells[0].get_text()] = []

                        elif cells[0].get_text() not in schedule_json:
                            schedule_json[list(schedule_json.keys())[-1]] = list_json
                            schedule_json[cells[0].get_text()] = []
                            list_json = []

                        sub = {"time": None, "remarks": None, "subject": None, "lecture-practice": None,
                               "room": None, "teacher": None, "date": None}

                        for i in range(1, len(cells)):
                            if i == 3:
                                subject_teacher = cells[i].get_text("|").split("|")
                                if len(subject_teacher) == 1:
                                    sub[key_sub[i]] = " ".join(subject_teacher)
                                    sub["teacher"] = ""
                                    sub["date"] = ""
                                else:
                                    if any(map(str.isdigit, subject_teacher[-1])) and len(subject_teacher) == 3:
                                        sub[key_sub[i]] = " ".join(subject_teacher[:-2])
                                        sub["teacher"] = subject_teacher[-2]
                                        sub["date"] = subject_teacher[-1]
                                    elif any(map(str.isdigit, subject_teacher[-1])) and subject_teacher[-1][
                                        0].istitle():
                                        sub[key_sub[i]] = subject_teacher[0]
                                        idx = subject_teacher[-1].find("(")
                                        sub["teacher"] = subject_teacher[-1][:idx - 1]
                                        sub["date"] = subject_teacher[-1][idx:]
                                    elif any(map(str.isdigit, subject_teacher[-1])) and subject_teacher[-1].startswith(
                                            "("):
                                        sub[key_sub[i]] = subject_teacher[0]
                                        sub["teacher"] = ''
                                        if 'вместо' in subject_teacher[-1]:
                                            #"(27.04 вместо 31.05)"
                                            new = subject_teacher[-1].split(' вместо ')[0] + ')'
                                            date = subject_teacher[-1].split()[-1][:-1].replace(' ', '').split(',')
                                            for da in date:
                                                day_m = da.replace('0', '').split('.')
                                                d = datetime(datetime.now().year, int(day_m[1]), int(day_m[0]))
                                                d_w = day_of_week[d.weekday()]
                                                data = schedule_json[d_w]
                                                for j, v in enumerate(data):
                                                    if v["subject"] == sub["subject"]:
                                                        if 'кроме' not in data[j]['date']:
                                                            if data[j]['date'] != '':
                                                                data[j]['date'] += ' (кроме ' + da + ')'
                                                            else:
                                                                data[j]['date'] += '(кроме ' + da + ')'
                                                        else:
                                                            many_date = re.findall(r'\([^()]+\)', data[j]['date'])
                                                            full = []
                                                            for p in many_date:
                                                                if 'кроме' in p:
                                                                    l = p.replace(')', '')
                                                                    l += da + ')'
                                                                    full.append(l)
                                                                    continue
                                                                full.append(p)

                                                            data[j]['date'] = ' '.join(full)

                                            sub["date"] = new
                                        else:
                                            sub["date"] = subject_teacher[-1]
                                    else:
                                        sub[key_sub[i]] = " ".join(subject_teacher[:-1])
                                        if subject_teacher[-1].istitle():
                                            sub["teacher"] = subject_teacher[-1]
                                        else:
                                            sub["teacher"] = ""
                                            sub["time"] = subject_teacher[-1]
                                        sub["date"] = ""
                            else:
                                sub[key_sub[i]] = cells[i].get_text()
                        list_json.append(sub)

                if list_json:
                    schedule_json[list(schedule_json.keys())[-1]] = list_json
                    list_json = []

                json.dump(schedule_json, file, ensure_ascii=False, indent=4)


def download_subgroups():
    host, conn, groups = connect_data()

    subgroups_letter = {}

    file_path = f"../subgroups.json"

    with open(file_path, "w", encoding='utf-8') as file:
        for k in range(1, 5):
            subgroups_letter.update({f"{k}": {}})
            for g in groups:
                subgroups_letter[f'{k}'].update({f"{g}": ''})

                if isinstance(g, int):
                    url = f'/ru/raspisanie-zanyatij/dnevnoe-otdelenie/{k}-kurs/{g}-gruppa/'
                else:
                    url = f'/ru/raspisanie-zanyatij/dnevnoe-otdelenie/{k}-kurs/{g}/'

                conn.request("GET", url, headers={"Host": host})
                r1 = conn.getresponse()

                if r1.status == 200:
                    data = r1.read()
                else:
                    print(f'Ошибка при скачивании данных. Код ошибки: {r1.status}')
                    conn.close()
                    continue

                soup = BeautifulSoup(data, "html.parser")

                table_rows = soup.find_all("tr")  # Найдите все строки таблицы

                sb = []

                for row in table_rows:
                    cells = row.find_all("td")  # все ячейки в строке

                    if len(cells) >= 5:  # Предполагаем, что нужно как минимум пять ячеек

                        subject_teacher = cells[2].get_text(" ").replace('/', ' ').split(" ")
                        for i in subject_teacher:
                            if i and i not in ['2н', '1н']:
                                sb.extend([i])

                sb = list(dict.fromkeys(sb))
                sb.sort()

                subgroups_letter[f'{k}'][f"{g}"] = sb

        json.dump(subgroups_letter, file, ensure_ascii=False, indent=4)

