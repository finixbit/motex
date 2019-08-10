
def int_to_hex(int_value):
    if not isinstance(int_value, int):
        raise ValueError(int_value)

    encoded = format(int_value, 'x')
    encoded = encoded.zfill(16)
    return ''.join([encoded])


def hex_to_int(hex_value):
    if not isinstance(hex_value, str):
        raise ValueError(hex_value)
    return int(hex_value, 16)