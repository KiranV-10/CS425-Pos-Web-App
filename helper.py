import decimal


def get_serializable_data(result):
    for row in result:
        row = get_serializable_item(row)
    return result


def get_serializable_item(row):
    for key, value in row.items():
        if isinstance(value, decimal.Decimal):
            row[key] = float(value)
    return row
