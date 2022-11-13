""""Author: Ruslan Khairutdinov onsunday1703@gmail.com"""
import datetime
import os
import re

import openpyxl
from bs4 import BeautifulSoup

from edutatar.settings import FILES_DIR
from journal_parser.JournalParser.edutatarauth import edu_auth
from journal_parser.JournalParser.get_journal import get_journal_info
from journal_parser.JournalParser.params import Params


def get_years(session):
    r = session.get("https://edu.tatar.ru/school")
    html = BeautifulSoup(r.text, "html.parser")

    h3 = html.find("h3")
    years = list(map(int, re.findall(r"\d+", h3.text)))

    return years


def execute(params):

    params = Params(params)

    print(params.login, params.password)
    session = edu_auth(params.login, params.password)
    session.get("https://edu.tatar.ru")

    years = get_years(session)

    table = openpyxl.Workbook()

    for class_num in range(params.class1, params.class2 + 1):
        r = session.get(
            "https://edu.tatar.ru/school/journal/select_edu_class?number={}".format(
                class_num
            )
        )
        soup = BeautifulSoup(r.text, "html.parser")

        grades = []
        links_to_journal = []

        lis = soup.find("div", {"class": "h"}).find_all("li")

        for li in lis:
            grade = li.text.split(maxsplit=1)[0].strip()
            grades.append(grade)

        for tag in soup.find_all("a", href=True):
            if tag.text == "Журнал класса":
                links_to_journal.append(tag["href"])

        grades_dict = dict(zip(grades, links_to_journal))

        for grade in grades_dict.keys():
            class_id = re.findall(r"\d+", grades_dict[grade])[0]
            r = session.get(grades_dict[grade])
            soup = BeautifulSoup(r.text, "html.parser")

            subject_ids = []
            for option in soup.find("select", id="criteria").find_all(
                name="option"
            ):  # extract subject values to get tables
                subject_ids.append(
                    (
                        option["value"],
                        [
                            s.strip().replace("\xa0", " ")
                            for s in option.text.split("/")
                        ],
                    )
                )

            print("Проверка {}".format(grade))

            sheet = table.create_sheet(grade)
            sheet.append(["Учитель", "Предмет", "Четверть/Полугодие", "Дата", "Ошибка"])

            for subject in subject_ids:
                if class_num > 9:
                    for term in range(params.term1 // 3 + 1, params.term2 // 3 + 2):
                        year = years[term - 1]
                        data = {
                            "sheet": sheet,
                            "session": session,
                            "term": term,
                            "criteria": subject,
                            "class_id": class_id,
                            "year": year,
                            "params": params,
                        }
                        if not get_journal_info(data):
                            break
                else:
                    for term in range(params.term1, params.term2 + 1):
                        year = years[term // 3]
                        data = {
                            "sheet": sheet,
                            "session": session,
                            "term": term,
                            "criteria": subject,
                            "class_id": class_id,
                            "year": year,
                            "params": params,
                        }
                        if not get_journal_info(data):
                            break

    minute = datetime.datetime.now().minute
    if minute < 10:
        minute = "0{}".format(minute)

    filename = "{0} {1}-{2}.xlsx".format(
        params.login, datetime.datetime.now().hour, minute
    )
    filepath = os.path.join(FILES_DIR, filename)
    table.save(filepath)

    return filename
