def get_value(report, year, column):

    year_index = -1
    column_index = -1
    if year in report['columns'][1:]:
        year_index = report['columns'][1:].index(year)
    else:
        return None

    if column in report['data'][0]:
        column_index = report['data'][0].index(column)
    else:
        return None

    return report['data'][year_index+1][column_index]


