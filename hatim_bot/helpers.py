from hatim_bot.models import Reader

def standings_generator(readers, count, filler):

    my_readers = iter(readers)
    place = 0
    prev_read_c = -1

    c = 0
    while c < count:
        try:
            reader = next(my_readers)

            if reader.read_counter != prev_read_c:
                place += 1
                prev_read_c = reader.read_counter
                yield (place, reader)
            else:
                yield (filler, reader)
            c += 1
        except StopIteration:
            return


def create_standings_table(reader, all_readers, count=10, filler='='):
    table = '*Место   Прочитано глав*\n'

    standings = standings_generator(all_readers, count, filler)

    reader_in = False
    for place, reader_ in standings:

        row = '\n      {}                {}'.format(place, reader_.read_counter)

        if reader == reader_:
            row = '*' + row + '*  <<'
            reader_in = True

        table += row

    if not reader_in:
        table += '\n      ...\n*      {}               {}* <<'.format(list(all_readers).index(reader) + 1, reader.read_counter)

    return table

def grab_name(func):

    def wrapper(message, *args, **kwargs):

        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username

        reader = Reader.objects.get(tg_id=message.from_user.id)
        if not any((reader.first_name, reader.last_name, reader.username)) and any((first_name, last_name, username)):

            if first_name:
                reader.first_name = first_name
            if last_name:
                reader.last_name = last_name
            if username:
                reader.username = username
            reader.save()
        return func(message, *args, **kwargs)

    return wrapper