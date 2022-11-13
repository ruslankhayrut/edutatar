""""Author: Ruslan Khairutdinov onsunday1703@gmail.com"""
import datetime
import locale
import re

from .params import CONTROL_WORKS, MARKS, MARKS_COLUMN_TYPES

locale.setlocale(locale.LC_ALL, "")


def fill_checker(sheet, page_data, params):
    subject = page_data["subject"]
    term_number = page_data["term"]

    teacher = page_data["teacher"]

    days = page_data["dates"]
    lessons = page_data["lessons"]

    marks = page_data["marks"]["common"]
    term_marks = page_data["marks"]["term_marks"]
    average_marks = page_data["marks"]["average_marks"]
    students_count = page_data["students_count"]

    row_pattern = [teacher, subject, term_number]

    warnings = []

    """Term marks validation"""
    if term_marks and params.check_term_marks:

        MINIMAL_FOR_5 = params.min_for_5
        MINIMAL_FOR_4 = params.min_for_4
        MINIMAL_FOR_3 = params.min_for_3

        for i in range(len(average_marks)):
            if average_marks[i] and term_marks[i]:
                if average_marks[i] >= MINIMAL_FOR_5 and term_marks[i] != 5:
                    date = ""
                    w = "Несоответствие средней и четвертной оценок. Строка {}".format(
                        i + 1
                    )
                    pattern = row_pattern + [date, w]
                    warnings.append(pattern)

                elif (
                    MINIMAL_FOR_4 <= average_marks[i] < MINIMAL_FOR_5
                    and term_marks[i] != 4
                ):
                    date = ""
                    w = "Несоответствие средней и четвертной оценок. Строка {}".format(
                        i + 1
                    )
                    pattern = row_pattern + [date, w]
                    warnings.append(pattern)

                elif (
                    MINIMAL_FOR_3 <= average_marks[i] < MINIMAL_FOR_4
                    and term_marks[i] != 3
                ):
                    date = ""
                    w = "Несоответствие средней и четвертной оценок. Строка {}".format(
                        i + 1
                    )
                    pattern = row_pattern + [date, w]
                    warnings.append(pattern)

            elif not average_marks[i]:
                date = ""
                w = "Нет среднего балла. Строка {}".format(i + 1)
                pattern = row_pattern + [date, w]
                warnings.append(pattern)

    if not params.only_term:
        for i in range(len(days)):
            l_type = lessons[i]["type"]
            l_meta = lessons[i]["meta"]

            date = datetime.datetime.strftime(days[i], "%d %B")

            try:
                next_l_type = lessons[i + 1]["type"]
            except IndexError:
                next_l_type = "РО"

            try:
                next_day = days[i + 1]
            except IndexError:
                next_day = days[i]

            """Validating lesson types"""
            if (
                params.check_RO
                and l_type in CONTROL_WORKS
                and days[i] != next_day
                and next_l_type != "РО"
            ):
                w = "После КР или Диктанта не работа над ошибками"
                pattern = row_pattern + [date, w]
                warnings.append(pattern)

            """Validating lesson topic and task"""
            if params.check_meta and l_meta:
                if not l_meta[0].startswith("Тема") or not l_meta[1].startswith(
                    "Задание"
                ):
                    w = "Нет Темы урока или ДЗ"
                    pattern = row_pattern + [date, w]
                    warnings.append(pattern)

            """Filling validator"""
            if params.check_lessons_fill:
                mrks = 0
                filled = 0
                for row in marks:
                    if row[i]:
                        filled += 1
                    if row[i] in MARKS:
                        mrks += 1

                """Types with marks row validator"""
                if l_type in MARKS_COLUMN_TYPES and not (
                    l_type == "ПР" and subject.startswith(params.allowed_not_row)
                ):
                    if (
                        filled != students_count
                        and days[i] + datetime.timedelta(days=8) < datetime.date.today()
                    ):
                        w = "Должен быть ряд оценок"
                        pattern = row_pattern + [date, w]
                        warnings.append(pattern)

                """Regular lessons fill validator"""
                if (
                    l_type not in MARKS_COLUMN_TYPES
                    or (l_type == "ПР" and subject.startswith(params.allowed_not_row))
                ) and round(
                    mrks / students_count, 2
                ) < params.lesson_percent / 100 - 0.01:
                    if (
                        l_type in ("Р", "П")
                        and days[i] + datetime.timedelta(days=8) < datetime.date.today()
                    ):
                        w = "Количество оценок меньше требуемого"
                        pattern = row_pattern + [date, w]
                        warnings.append(pattern)

        """Student's marks in the term percent and double 2 validator"""
        if params.check_students_fill or params.check_double_two:
            for row in range(len(marks)):
                total = len(marks[row])
                only_marks = [m for m in marks[row] if m in MARKS]
                only_ms = len(only_marks)

                if total:
                    if params.check_students_fill:
                        if only_ms / total < params.term_percent / 100:
                            date = ""
                            w = "У ученика мало оценок за четверть. Строка {}".format(
                                row + 1
                            )
                            pattern = row_pattern + [date, w]
                            warnings.append(pattern)

                    if params.check_double_two:
                        for i in range(only_ms - 1):
                            if only_marks[i] == 2 and only_marks[i + 1] == 2:
                                date = ""
                                w = "Две двойки подряд. Строка {}".format(row + 1)
                                pattern = row_pattern + [date, w]
                                warnings.append(pattern)

    for warning in warnings:
        sheet.append(warning)
    sheet.freeze_panes = sheet["A2"]
