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
        tdelta = timedelta(seconds = t)
        days = tdelta.days
        sdays = day * days
        delta = tdelta.seconds + sdays
        if delta < 2:
            return 'a second'
        elif delta < 60:
            return '{0} seconds'.format(int(delta))
        elif delta < self.hour:
            minutes = int(delta / 60.0)
            if minutes < self.prec:
                seconds = int(delta - 60*minutes)
                p = ''
                if minutes > 1:
                    p = 's'
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


def smart_time(t):
    from djpcms import sites
    settings = sites.settings
    if not settings:
        return
    if not isinstance(t,date):
        try:
            t = datetime.fromtimestamp(t)
        except:
            return t
    time = None
    if isinstance(t,datetime):
        ti = t.time()
        if ti:
            ts = 'H:i' if not settings else settings.TIME_FORMAT
            time = time_format(ti,ts)
            t = t.date()
            if t == date.today():
                return time
    ts = 'd M y' if not settings else settings.DATE_FORMAT
    day = format(d,ts)
    if time:
        day = '{0} {1}'.format(day,time)
    return day
