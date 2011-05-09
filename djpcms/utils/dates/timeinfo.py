from datetime import timedelta

__all__ = ['nicetimedelta']

fudge  = 1.25
hour   = 60.0 * 60.0
day    = hour * 24.0
week   = 7.0 * day
month  = 30.0 * day

def nicetimedelta(t):
    tdelta = timedelta(seconds = t)
    days    = tdelta.days
    sdays   = day * days
    delta   = tdelta.seconds + sdays
    if delta < fudge:
        return 'about a second'
    elif delta < (60.0 / fudge):
        return 'about %d seconds' % int(delta)
    elif delta < (60.0 * fudge):
        return 'about a minute'
    elif delta < (hour / fudge):
        return 'about %d minutes' % int(delta / 60.0)
    elif delta < (hour * fudge):
        return 'about an hour'
    elif delta < day:
        return 'about %d hours' % int(delta / hour)
    elif days == 1:
        return 'about 1 day'
    else:
        return 'about %s days' % days