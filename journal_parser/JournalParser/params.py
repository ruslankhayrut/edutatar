import re

MARKS = range(1, 6)
STR_MARKS = ('1', '2', '3', '4', '5')

CONTROL_WORKS = ('КР', 'Д')

MARKS_COLUMN_TYPES = ('КР', 'ЛР', 'СР', 'ПР', 'Д', 'С', 'И', 'Т', 'СД', 'З')


KEYS = ('check_RO', 'check_meta', 'check_lessons_fill', 'check_students_fill',
        'check_double_two', 'check_term_marks')

TO_FLOAT = ('min_for_5', 'min_for_4', 'min_for_3')
TO_INT = ('class1', 'class2', 'term1', 'term2', 'lesson_percent', 'term_percent')




class Params:
    def __init__(self, kwargs):
        self.set_attributes(kwargs)

    def set_attributes(self, kwargs):
        for key, val in kwargs.items():
            if key in TO_FLOAT:
                val = float(val)
                setattr(self, key, val)
            elif key in TO_INT:
                val = int(val)
                setattr(self, key, val)
            elif key == 'allowed_not_row' and val:
                allowed_not_row = re.findall('[А-Яа-яЁё]+', val)
                for e in range(len(allowed_not_row)):
                    allowed_not_row[e] = allowed_not_row[e][0].upper() + allowed_not_row[e][1:].lower()

                val = tuple(allowed_not_row)
                setattr(self, key, val)
            else:
                setattr(self, key, val)


        if self.class1 > self.class2:
            self.class2 = self.class1

        if self.term1 > self.term2:
            self.term2 = self.term1

        if (not self.check_RO and not self.check_meta and not self.check_lessons_fill
        and not self.check_students_fill and not self.check_double_two):
            self.only_term = True
        else:
            self.only_term = False