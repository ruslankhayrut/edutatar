import random
from .models import *

SUBJECTS = ["Русский язык", "Математика", "Английский язык", "Физика", "Химия",
            "Литература", "География", "Биология", "Родной язык", "Родная литература",
            "Информатика", "Физкультура", "История", "Обществознание",
            "Право", "Алгебра", "Геометрия", "Технология"]

# HOMEWORKS = dict(zip(SUBJECTS, ('Ничего не задано'.format(subj) for subj in SUBJECTS)))

HOMEWORKS = {
    'Русский язык': 'упражнение 7 на стр. 34',
    'Математика': '# 7, 10, 12 стр. 57',
    'География': 'прочитать параграф 16, ответить на вопросы в конце учебника',
    'Биология': 'доделать лабораторную работу, узнать виды растений',
    'Английский язык': 'ex. 10 page 23, learn new words',
    'Технология': 'доделать кормушку',
    'Родной язык': 'инша язырга'
}


def generate_fake_data(student):
    subj_items = []
    for s_name in SUBJECTS:
        marks_count = random.randrange(5, 10, 1)
        marks = [random.choice([3, 4, 5]) for i in range(marks_count)]
        m_string = ', '.join(str(m) for m in marks)
        subj_item = Subject(
            name=s_name, student=student, marks_string=m_string, homework=HOMEWORKS.get(s_name, 'Ничего не задано'))
        subj_items.append(subj_item)

    Subject.objects.bulk_create(subj_items)
    return
