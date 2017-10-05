
def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'B'][magnitude])


def dollar_value(num):
    return "$" + "{:.2f}".format(abs(num))


def percent_value(num):
    return "{:.2f}".format(abs(num)) + "%"


def dollar_change(num):
    return ("-" if num < 0 else "+") + dollar_value(num)


def percent_change(num):
    return ("-" if num < 0 else "+") + percent_value(num)
