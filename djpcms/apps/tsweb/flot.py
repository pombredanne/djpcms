from datetime import datetime, date

from dynts import Formatters
from dynts.utils.py2py3 import is_string
from dynts.utils.anyjson import JSONdatainfo, JSONobject
from dynts.formatters import BaseFormatter

EPOCH = 1970
_EPOCH_ORD = date(EPOCH, 1, 1).toordinal()


def pydate2flot(dte):
    year, month, day, hour, minute, second = dte.timetuple()[:6]
    days = date(year, month, 1).toordinal() - _EPOCH_ORD + day - 1
    hours = days*24 + hour
    minutes = hours*60 + minute
    seconds = minutes*60 + second
    if isinstance(dte,datetime):
        return 1000*seconds + 0.001*dte.microsecond
    else:
        return 1000*seconds


class MultiPlot(JSONdatainfo):
    '''Class holding several :class:`dynts.web.flot.Flot` instances.

    .. attribute:: plots

        list of :class:`dynts.web.flot.Flot` instances.

    .. attribute:: info

        Additional serialisable data
    '''
    def __init__(self, flot = None, info = None):
        super(MultiPlot,self).__init__(data = [], info = info)
        self.add(flot)

    def add(self, flot):
        '''Add a new :class:`dynts.web.flot.Flot` instance to :attr:`dynts.web.flot.MultiPlot.plots`.'''
        if isinstance(flot,Flot):
            self.data.append(flot)

    def todict(self):
        return {'type': 'multiplot',
                'info': self.info,
                'plots': [plot.todict() for plot in self.data]}


class Flot(JSONobject):
    '''A single plot which can be a timeseries or a XY plot.'''
    allowed_types = ['xy','timeseries','scatter']
    def __init__(self, name = '', type = None, shadowSize = None, **kwargs):
        if type not in self.allowed_types:
            type = 'xy'
        self.name   = name
        self.type   = type
        self.series = []
        df = {}
        self.options = df
        if shadowSize:
            df['shadowSize'] = shadowSize

    def add(self, serie):
        if isinstance(serie,Serie):
            self.series.append(serie)

    def todict(self):
        od = super(Flot,self).todict()
        od['series'] = [serie.todict() for serie in self.series]
        return od


class Serie(JSONobject):

    def __init__(self, label = '', data = None,
                 color = None, shadowSize = None, yaxis = 1, xaxis = 1,
                 extratype = None, **kwargs):
        self.label = label
        if data is None:
            data = ()
        if extratype == 'date':
            ndata = []
            for a,b,dt in data:
                ndata.append((a,b,pydate2flot(dt)))
            data = ndata
        self.data = data
        for k,v in kwargs.items():
            setattr(self,k,v)
        self.extratype = extratype
        if is_string(color):
            if not color.startswith('#'):
                color = '#%s' % color
        self.xaxis = xaxis
        self.yaxis = yaxis
        if color:
            self.color = color
        if shadowSize:
            self.shadowSize = shadowSize

    def __str__(self):
        return self.label
    __repr__ = __str__


class ToFlot(BaseFormatter):
    type = 'json'
    default = True

    def __call__(self, ts, container=None, desc=False, ordering=None,
                 series_info=None, **kwargs):
        '''Dump timeseries as a JSON string compatible with ``flot``'''
        pydate2flot = flot.pydate2flot
        result = container or flot.MultiPlot()
        series_info = self.get_serie_info(series_info)
        if istimeseries(ts):
            res = flot.Flot(ts.name, type='timeseries', **series_info)
            dates  = asarray(ts.dates())
            missing = settings.ismissing
            for name, serie in ts.named_series(ordering):
                info = self.get_serie_info(series_info,name)
                data = []
                append = data.append
                for dt,val in zip(dates,serie):
                    if not missing(val):
                        append([pydate2flot(dt),val])
                serie = flot.Serie(label = name, data = data, **info)
                res.add(serie)
        else:
            res = flot.Flot(ts.name)
            if ts.extratype:
                for name,serie in zip(ts.names(),ts.series()):
                    serie = flot.Serie(label = serie.name,
                                       data = serie.data,
                                       lines = {'show':serie.lines},
                                       points = {'show':True},
                                       scatter = {'show':serie.points},
                                       extratype = ts.extratype)
                    res.add(serie)
            else:
                for name,serie in zip(ts.names(),ts.series()):
                    serie = flot.Serie(label = serie.name,
                                       data = serie.data,
                                       lines = {'show':serie.lines},
                                       points = {'show':serie.points})
                    res.add(serie)
        result.add(res)
        return result

    def get_serie_info(self, serie_info, name = None):
        if not name:
            return series_info or {}
        else:
            return series_info.get(name,{})


Formatters['flot'] = ToFlot()
