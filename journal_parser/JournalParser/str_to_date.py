import datetime

m = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]
n = range(1, 13)

d = dict(zip(m, n))


def str_to_date(day, month, year):
    if day < 10:
        day = "0{}".format(day)

    s = str(day) + str(d[month]) + str(year)

    return datetime.datetime.strptime(s, "%d%m%Y").date()
