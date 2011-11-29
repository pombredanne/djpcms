'''Define some application urls templates as example
'''
import copy

from djpcms import views
from djpcms.utils.dates import MONTHS_3, MONTHS_3_REV, WEEKDAYS_ABBR, MONTHS
from djpcms.utils import force_str


__all__ = ['ArchiveApplication',
           'ArchiveView',
           'YearArchiveView',
           'MonthArchiveView',
           'DayArchiveView']


class ArchiveView(views.SearchView):
    '''
    Search view with archive subviews
    '''    
    def _date_code(self):
        return self.appmodel.date_code
    
    def content_dict(self, djp):
        c = super(ArchiveView,self).content_dict(djp)
        month = c.get('month',None)
        if month:
            c['month'] = self.appmodel.get_month_number(month)
        year = c.get('year',None)
        day  = c.get('day',None)
        if year:
            c['year'] = int(year)
        if day:
            c['day'] = int(day)
        return c
    
    def appquery(self, djp, **kwargs):
        qs       = super(ArchiveView,self).appquery(djp, **kwargs)
        kwargs   = djp.kwargs
        month    = kwargs.get('month',None)
        day      = kwargs.get('day',None)
        dt       = self._date_code()
        dateargs = {}
        if 'year' in kwargs:
            dateargs['%s__year' % dt] = int(kwargs['year'])
        
        if month:
            month = self.appmodel.get_month_number(month)
            if month:
                dateargs['%s__month' % dt] = month
    
        if day:
            dateargs['%s__day' % dt] = int(day)
            
        #qs = self.basequery(request, **kwargs)
        if dateargs:
            return qs.filter(**dateargs)
        else:
            return qs


class DayArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(DayArchiveView,self).__init__(*args,**kwargs)
    def title(self, djp):
        return djp.getdata('day')
    
    
class MonthArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(MonthArchiveView,self).__init__(*args,**kwargs)
    def title(self, djp):
        m = self.appmodel.get_month_number(djp.getdata('month'))
        return force_str(MONTHS[m])
                                          
    
class YearArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(YearArchiveView,self).__init__(*args,**kwargs)
    def title(self, djp):
        return djp.getdata('year')
    

class ArchiveApplication(views.Application):
    '''\
A :class:`djpcms.views.ModelApplication` wich defines archive views
based on a date field.
It needs to specify a new attribute either in the constructor or as
class attribute:

.. attribute:: date_code

    Name of field used to create archives
'''
    date_code     = None
    split_days    = False
    
    search = ArchiveView()
    year_archive  = YearArchiveView('<year>/',
                                    has_plugins = False)
    month_archive = MonthArchiveView('<month>/',
                                     parent_view = 'year_archive',
                                     has_plugins = False)
    day_archive   = DayArchiveView('<day>/',
                                   parent_view = 'month_archive',
                                  has_plugins = False)
    
    def __init__(self, *args, **kwargs):
        self.date_code = kwargs.pop('date_code',self.date_code)
        super(ArchiveApplication,self).__init__(*args, **kwargs)
    
    def orderquery(self, qs):
        return qs.order_by('-'+self.date_code)
        
    def get_month_value(self, month):
        return force_str(MONTHS_3.get(month))

    def get_month_number(self, month):
        try:
            return int(month)
        except:
            return MONTHS_3_REV.get(month,None)
        
    def yearurl(self, request, year, **kwargs):
        view = self.getview('year_archive')
        if view:
            return view(request, year = year, **kwargs).url
        
    def monthurl(self, request, year, month, **kwargs):
        view  = self.getview('month_archive')
        if view:
            month = self.get_month_value(month)
            return view(request, year = year, month = month, **kwargs).url
        
    def dayurl(self, request, year, month, day, **kwargs):
        view = self.getview('day_archive')
        if view:
            month = self.get_month_value(month)
            return view(request, year = year, month = month, day = day,
                        **kwargs).url
        
    def data_generator(self, djp, data):
        '''Modify the standard data generation method so that links
to date archive are generated'''
        request  = djp.request
        prefix   = djp.prefix
        wrapper  = djp.wrapper
        date     = None
        render   = loader.render
        Context  = loader.context_class
    
        for obj in data:
            content = self.object_content(djp, obj)
            dt      = getattr(obj,self.date_code)
            ddate   = dt.date()
            if self.split_days and (not date or date != ddate):
                urlargs = djp.kwargs.copy()
                urlargs.pop('year',None)
                urlargs.pop('month',None)
                urlargs.pop('day',None)
                content['year']  = {'url': self.yearurl(request,dt.year,**urlargs),
                                    'value': dt.year}
                content['month'] = {'url': self.monthurl(request,dt.year,dt.month,**urlargs),
                                    'value': force_str(MONTHS[dt.month])}
                content['day']   = {'url': self.dayurl(request,dt.year,dt.month,dt.day,**urlargs),
                                    'value': dt.day}
                content['wday']  = force_str(WEEKDAYS_ABBR[dt.weekday()])
                date = ddate
            yield render(self.get_item_template(obj, wrapper),
                         Context(content))
    
    