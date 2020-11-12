import random
from .models import *

SUBJECTS = ["Русский язык", "Математика", "Английский язык", "Физика", "Химия",
              "Литература", "География", "Биология", "Татарский язык", "Татарская литература",
              "Информатика", "Физкультура", "История", "Обществознание",
              "Право", "Алгебра", "Геометрия"]

HOMEWORKS = dict(zip(SUBJECTS, (f'ДЗ по {subj}' for subj in SUBJECTS)))


def generate_fake_data(student):

    subj_items = []
    for s_name in SUBJECTS:
        marks_count = random.randrange(5, 10, 1)
        marks = [random.choice([3, 4, 5]) for i in range(marks_count)]
        m_string = ', '.join(str(m) for m in marks)
        subj_item = Subject(name=s_name, student=student, marks_string=m_string, homework=HOMEWORKS[s_name])
        subj_items.append(subj_item)

    Subject.objects.bulk_create(subj_items)
    return



