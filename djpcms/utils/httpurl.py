'''Use pulsar httpurl and multiform'''
from pulsar.utils.httpurl import *
from pulsar.utils.multipart import parse_form_data
from pulsar.utils.structures import MultiValueDict


def _gen_query(query_string, encoding):
    # keep_blank_values=True
    for key, value in parse_qsl((query_string or ''), True):
        yield to_string(key, encoding, errors='replace'),\
              to_string(value, encoding, errors='replace')


def QueryDict(query_string, encoding='utf-8'):
    if query_string:
        return MultiValueDict(_gen_query(query_string, encoding))
    else:
        return MultiValueDict()


def remove_end_slashes(url):
    if url.endswith('/'):
        url = url[:-1]
    if url.startswith('/'):
        url = url[1:]
    return url


def urlbits(url):
    url = remove_end_slashes(url)
    return url.split('/')


def urlfrombits(bits):
    if bits:
        return '/%s/' % '/'.join(bits)
    else:
        return '/'
