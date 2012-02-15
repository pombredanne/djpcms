from datetime import timedelta, date, datetime

from .dateformat import time_format, format

__all__ = ['NiceTimeDelta',
           'nicetimedelta',
           'smart_time']

fudge  = 1.25


class NiceTimeDelta(object):
    
    def __init__(self, fudge = 1.25):
        self.fudge = fudge
        self.hour = 60.0 * 60.0
        self.day = self.hour * 24.0
        self.week = 7.0 * self.day
        self.month = 30.0 * self.day
        self.prec = int(60*(fudge-1))
        
    def __call__(self, t):
        fudge = self.fudge
        hour = self.hour
        day = self.day
        tdelta = timedelta(seconds = t or 0)
        days = tdelta.days
        sdays = day * days
        delta = tdelta.seconds + sdays
        if delta < 2:
            return 'a second'
        elif delta < 60:
            return '{0} seconds'.format(int(delta))
        elif delta < self.hour:
            minutes = int(delta / 60.0)
            p = '' if minutes == 1 else 's'
            seconds = int(delta - 60*minutes)
            if minutes < self.prec and seconds > 1:
                return '{0} minute{1} and {2} seconds'.format(minutes,p,seconds)
            else:
                return '{0} minutes'.format(minutes)
        elif delta < (hour * fudge):
            return 'an hour'
        elif delta < day:
            return '%d hours' % int(delta / hour)
        elif days == 1:
            return '1 day'
        else:
            return '%s days' % days
    
    
nicetimedelta = NiceTimeDelta()
empty_dict = {}

def smart_time(t, dateformat = None, timeformat = None, settings = None):
    '''Format a date or datetime.'''
    settings = settings or empty_dict
    if not isinstance(t,date):
        try:
            t = datetime.fromtimestamp(t)
        except:
            return t
    time = None
    if isinstance(t,datetime):
        ti = t.time()
        if ti:
            if not timeformat:
                timeformat = settings.get('TIME_FORMAT','H:i')
            time = time_format(ti,timeformat)
            t = t.date()
            if t == date.today():
                return time
    if not dateformat:
        dateformat = settings.get('DATE_FORMAT','d M y')
        
    day = format(t,dateformat)
    if time:
        day = '{0} {1}'.format(day,time)
    return day
