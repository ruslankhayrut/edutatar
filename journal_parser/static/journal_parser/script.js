function lessons_fill() {
    c = document.getElementById('check_lessons_fill')
    inpt = document.getElementById('lesson_percent')
    anotr = document.getElementById('allowed_not_row')

    if (c.checked) {
        anotr.disabled = false;
        inpt.disabled = false;

    } else {
        anotr.disabled = true;
        inpt.disabled = true;

    }
}

function students_fill() {
    c = document.getElementById('check_students_fill')
    inpt = document.getElementById('term_percent')

    if (c.checked) {

        inpt.disabled = false;
    } else {

        inpt.disabled = true;
    }
}

function term_marks() {
    c = document.getElementById('check_term_marks')

    for (var i = 3; i <=5; i++) {
        id = `min_for_${i}`;
        inpt = document.getElementById(id);
        if (c.checked) {
            inpt.disabled = false;
        } else {
            inpt.disabled = true;
        };
    };
}


function revoke_confirm(f) {
    if (confirm('Вы уверены, что хотите отменить проверку?')) {
        return true
    } else {
        return false
    }
}
