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