""""Author: Ruslan Khairutdinov onsunday1703@gmail.com"""

import datetime
from bs4 import BeautifulSoup
from .fill_checker import fill_checker
from .str_to_date import str_to_date, m
from .constants import STR_MARKS

def get_journal_info(data, moved_students=False):

    session = data['session']
    term = data['term']
    criteria = data['criteria']
    class_id = data['class_id']
    year = data['year']
    params = data['params']


    journal_url = 'https://edu.tatar.ru/school/journal/school_editor?term={0}' \
                  '&criteria={1}&edu_class_id={2}&' \
                  'show_moved_pupils={3}'.format(term, criteria[0], class_id, int(moved_students))
    journal = session.get(journal_url)
    html = BeautifulSoup(journal.text, 'lxml')

    if criteria[1][1].startswith('Электив'):
        return False

    teacher = html.find('div', {'class': 'line last'})
    if teacher:
        try:
            teacher = teacher.text.strip().split(maxsplit=1)[1]
        except IndexError as e:
            print(journal_url, "Нет учителя и учеников.", e)
            return False


    pages = html.find('div', {'class': 'pages'})

    pages = [p for p in pages.text.split() if (p.isdigit() or p == '>>')]

    if pages:
        if pages[-1] != '>>':
            last_page = int(pages[-1])
        else:
            r = session.get('https://edu.tatar.ru/school/journal/school_editor?term={0}' \
                  '&criteria={1}&edu_class_id={2}&' \
                  'show_moved_pupils={3}&page={4}'.format(term, criteria[0], class_id, int(moved_students), int(pages[-2])+1))
            html = BeautifulSoup(r.text, 'lxml')
            pages = html.find('div', {'class': 'pages'})
            pages = [p for p in pages.text.split() if p.isdigit()]
            last_page = int(pages[-1])
    else:
        last_page = 1


    pagedata = {'teacher': teacher, 'term': int(term), 'subject': criteria[1][1], 'months': [], 'dates': [], 'lessons': [],
                'marks': {'common': [], 'term_marks': [], 'average_marks': []}}

    cont = True

    for page in range(1, last_page+1): #look through the pages in the quarter

        journal_url = 'https://edu.tatar.ru/school/journal/school_editor?term={0}' \
                      '&criteria={1}&edu_class_id={2}&' \
                      'show_moved_pupils={3}&page={4}'.format(term, criteria[0], class_id, int(moved_students), page)
        journal = session.get(journal_url)
        html = BeautifulSoup(journal.text, 'lxml')


        months = get_months(html)
        pagedata['months'] += months

        datenums = get_dates(html)

        dates, stop = create_dates(months, datenums, year)

        meta_check = params.get('check_meta')
        lessons = get_lessons(html, len(dates), meta_check)

        pagedata['dates'] += dates
        pagedata['lessons'] += lessons

        req_marks = {
            'common': (params.get('check_lessons_fill'), params.get('check_students_fill'),
                       params.get('check_double_two')),
            'term': params.get('check_term_marks')
        }

        marks, term_marks, average_marks = get_marks(html, page, len(dates), req_marks)
        if page == 1:
            pagedata['marks']['common'] += marks
            if term_marks and term_marks.count(None) != len(term_marks):
                pagedata['marks']['term_marks'] += term_marks
                pagedata['marks']['average_marks'] += average_marks

            if len(marks) > 0:
                pagedata['students_count'] = len(marks)
            else:
                return False

        else:
            st = pagedata['students_count']
            # assert st == len(marks), ('Количество учеников на страницах не совпадает', journal_url)
            for i in range(st):
                pagedata['marks']['common'][i] += marks[i]

        if stop:
            cont = False
            break

    """Check quarter columns if filled properly"""
    fill_checker(sheet=data['sheet'], page_data=pagedata, params=data['params'])

    return cont


def get_months(html):
    months_list = []
    months = html.find(text='Ученики').findAllNext('td', text=lambda text: text in m)
    for month in months:
        days = int(month['colspan'])
        months_list.append((month.text, days))
    return months_list


def get_dates(html):
    dts = html.find('table', {'class': 'table'}).findNext('tr').findNext('tr').find_all('td')
    datenums = []
    for date in dts:
        joint = int(date['colspan'])
        for i in range(joint):
            datenums.append(int(date.text))
    return datenums


def create_dates(months, dates, year):
    arr = []
    stop = False
    k = 0
    for month in months:
        for i in range(month[1]): #colspan
            date = str_to_date(dates[k], month[0], year)
            if date > datetime.date.today(): #don't parse the future
                stop = True
                return arr, stop
            arr.append(date)
            k += 1
    return arr, stop


def get_lessons(html, n, meta_check):
    lessons = html.find('table', {'class': 'table'}).findNext('tr').findNext('tr').findNext('tr').find_all('td')
    lesson_types = []
    for lesson in lessons:
        if meta_check:
            try:
                meta = lesson.get('title').split('\n\n')[:2]
            except AttributeError:
                meta = None
            if len(meta) != 2:
                meta = None
        else:
            meta = None
        lesson_types.append({'type': lesson.text, 'meta': meta})
    return lesson_types[:n]

def get_marks(html, page, n, req_marks):
    marks = []
    rows = html.find('tbody').findAllNext('tr')
    term_marks = []
    average_marks = []
    for row in rows[:-2]: #remove service rows
        if 'on' in req_marks['common']: # get common marks, if none is checked don't get them
            marks_row = []
            cols = row.find_all('td', {'class': 'mark'})
            for col in cols:
                mark = col.text.strip()
                if mark in STR_MARKS:
                    mark = int(mark)
                marks_row.append(mark)
            marks_row = marks_row[:n]
            marks.append(marks_row)

        if page == 1 and req_marks['term']: # if term marks to be collected
            try:
                average = float(row.find_all('td', {'class': 'mark'})[-1].text.strip().replace(',', '.'))
            except ValueError:
                average = None
            average_marks.append(average)

            try:
                tm = row.find('td', {'class': 'term-mark db-border-left'}).findNext('div').text.strip()
                if tm in STR_MARKS:
                    term_mark = int(tm)
                    term_marks.append(term_mark)
                else:
                    term_marks.append(None)
            except AttributeError:
                pass

    return marks, term_marks, average_marks