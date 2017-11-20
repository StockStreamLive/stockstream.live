
def compute_change_decimal(from_value, to_value):
    if from_value == 0 and to_value == 0:
        return 0
    from_value = 1 if from_value == 0 else from_value
    difference = (to_value - from_value)
    decimal_change = (difference / from_value)
    return decimal_change
