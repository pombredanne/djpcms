import sys
from math import fabs

def significant(number, n=None):
    '''Round a number up to a given number ``n`` of significant figures.
Rounding to ``n`` significant digits is a more general-purpose technique
than rounding to ``n`` decimal places, since it handles numbers
of different scales in a uniform way.'''
    n = n if n is not None else 4
    r = '%.' + str(n) + 'g'
    v = float(r % float(number))
    i = int(v)
    return i if i == v else v

def significant_format_old(number, n=4):
    """Format a number according to a given number of significant figures."""
    number = significant(number, n)
    str_number = str(number)
    anumber = fabs(number)
    # bail out early
    if anumber < 1000:
        return str_number
    if '.' in str_number:
        int_part, dec_part = str_number.split('.')
    else:
        int_part, dec_part = str_number, ''
    sign = '-' if number < 0 else ''
    remaining = int(fabs(int(int_part)))
    bits = []
    while remaining:
        bits.append(str(remaining % 1000))
        remaining = remaining // 1000
    int_part = '%s%s' % (sign,','.join(reversed(bits)))
    if dec_part:
        return '%s.%s' % (int_part, dec_part)
    else:
        return int_part

if sys.version_info >= (2,7):
    def significant_format(number, n=3):
        number = significant(number, n)
        return '{:,}'.format(number)
else:
    significant_format = significant_format_old