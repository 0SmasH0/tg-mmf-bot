from datetime import datetime, timedelta
import math


def check_saturday_sunday() -> bool:
    today = datetime.now().today()
    if today in (5, 6):
        return True
    else:
        return False


def correct_date_for_week(date: datetime) -> datetime:
    sem = date

    day = sem.weekday()
    if day >= 5:
        earlier_datetime = sem + timedelta(days=7 - day)

    elif day != 0:
        earlier_datetime = sem - timedelta(days=day)

    else:
        earlier_datetime = sem

    return earlier_datetime


def get_number_week() -> str:
    data = {
        "1sem": [
            correct_date_for_week(datetime(datetime.now().year, 9, 1)),
            datetime(datetime.now().year, 12, 30)
        ],
        "2sem": [
            correct_date_for_week(datetime(datetime.now().year, 2, 4)),
            datetime(datetime.now().year, 6, 10)
        ]
    }

    current_datetime = datetime.now()
    day_of_week = current_datetime.weekday()

    if day_of_week >= 6:
        d = timedelta(7 - day_of_week)
        current_datetime += d

    for i in data:
        if data[i][0] <= current_datetime <= data[i][1]:
            days = (current_datetime - data[i][0]).days

            if math.ceil(days / 7) == int(days / 7):
                w = int(days / 7) + 1
            else:
                w = math.ceil(days / 7)
            if w % 2 == 0:
                w_d = '2н'
                break
            else:
                w_d = '1н'
                break

    with open('subgroups.json', 'w') as f:
        f.write(w_d)


def correct_date(date: str, time: datetime) -> (datetime, datetime):
    date = date.replace("(", "").replace(")", "")

    if date.rfind(' ') != -1 and not date[-1].isdigit():
        var = date.rfind(' ')
        if str(date[:var]) not in ['с', 'кроме', 'до', 'c']:
            date = date[:var]

    date_format = "%d.%m.%Y"
    year = time.year

    # (27.03 нрпта) (18.04) (кроме 29.03) (с 01.01) (до 23.03)  (08.02-07.03) (14.02, 28.02, 13.03)
    if '-' in date:
        dates_str = date.split('-')
        date1 = datetime.strptime(dates_str[0] + f'.{str(year)}', date_format)
        date2 = datetime.strptime(dates_str[1] + f'.{str(year)}', date_format) + timedelta(hours=23, minutes=59,
                                                                                           seconds=59)

    elif "с" in date:
        dates_str = date[2:]
        date1 = datetime.strptime(dates_str + f'.{str(year)}', date_format)
        date2 = datetime.strptime(dates_str + f'.{str(year + 1)}', date_format)

    elif "до" in date:
        dates_str = date[3:]
        date1 = datetime.strptime(dates_str + f'.{str(year - 1)}', date_format)
        date2 = datetime.strptime(dates_str + f'.{str(year)}', date_format) + timedelta(hours=23, minutes=59,
                                                                                        seconds=59)

    elif "кроме" in date:
        dates_str = date[6:].replace(' ', '').split(',')
        for i in dates_str:
            dat1 = datetime.strptime(i + f'.{str(year)}', date_format)
            dat2 = datetime.strptime(i + f'.{str(year)}', date_format) + timedelta(hours=23, minutes=59, seconds=59)
            if dat1 <= time <= dat2:
                dat = datetime(9999, 1, 1)
                return dat, dat
        return datetime(1000, 1, 1), datetime(9999, 1, 1)

    elif "," in date:
        dates_str = date.replace(' ', '').split(',')
        for i in dates_str:
            dat1 = datetime.strptime(i + f'.{str(year)}', date_format)
            dat2 = datetime.strptime(i + f'.{str(year)}', date_format) + timedelta(hours=23, minutes=59, seconds=59)
            if dat1 <= time <= dat2:
                return dat1, dat2
        return datetime(9999, 1, 1), datetime(9999, 1, 1)

    else:
        date1 = datetime.strptime(date + f'.{str(year)}', date_format)
        date2 = datetime.strptime(date + f'.{str(year)}', date_format) + timedelta(hours=23, minutes=59, seconds=59)

    return date1, date2
