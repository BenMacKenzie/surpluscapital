def get_value(report, year, column):

    year_index = -1
    column_index = -1
    for c in report['columns'][1:]:
        year_index += 1
        if year == c:
            break

    for c in report['data'][0]:
        column_index += 1
        if column == c:
            break

    if year_index == -1 or column_index == -1:
        return None

    return report['data'][year_index+1][column_index]


