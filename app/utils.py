import imghdr
import csv


def atoi(text):
    """ Convert a string into an integer numerical representation """

    return int(text) if text.isdigit() else text


def natural_keys(text):
    """ Call atoi on text """

    return [ atoi(c) for c in re.split('(\d+)', text) ]


def validate_image(stream):
    """ Validate that the image is jpg """

    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')
