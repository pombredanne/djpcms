from datetime import date, datetime

from djpcms.utils.text import nicename
from djpcms.utils.dates import format as date_format
from djpcms.utils import force_str, significant_format

from .icons import yes,no

__all__ = ['nicerepr','NONE_VALUE']

NONE_VALUE = '(None)'
DEFAULT_DATE_FORMAT = 'd M y'
DEFAULT_DATETIME_FORMAT = DEFAULT_DATE_FORMAT + ' H:i'


def nicerepr(val,
             nd = 3,
             none_value = NONE_VALUE,
             dateformat = DEFAULT_DATE_FORMAT,
             datetime_format = DEFAULT_DATETIME_FORMAT):
    '''Prettify a value to be displayed in html'''
    if val is None:
        return empty_value
    elif isinstance(val,datetime):
        time = val.time()
        if not time:
            return date_format(val.date(),dateformat)
        else:
            return date_format(val,datetime_format)
    elif isinstance(val,date):
        return date_format(val,dateformat)
    elif isinstance(val,bool):
        if val:
            return yes(val)
        else:
            return no(val)
    else:
        try:
            return significant_format(val, n = nd)
        except TypeError:
            return val
    
