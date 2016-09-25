import gzip

import classes


def load_map(filepath):
    classes.clear()
    with open(filepath, "rb") as file:
        for byte in degzip(file.read()):
        hex_byte = hex(byte)[2:]
            while len(hex_byte) < 2:
                hex_byte = '0' + hex_byte
            classes.data.append(hex_byte)
        classes.map_was_loaded = True


def delete_map():
    classes.clear()


def degzip(data):
    try:
        ret = gzip.decompress(data)
    except OSError:
        ret = data
    return ret


def set_encoding(codec):
    classes.Glo = codec
