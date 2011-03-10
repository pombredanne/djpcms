from datetime import date, datetime

from djpcms import sites, nodata
from djpcms.utils.dates import format as date_format
from djpcms.utils import force_str, significant_format, EMPTY_VALUE
from djpcms.template import loader, conditional_escape

__all__ = ['BaseOrmWrapper',
           'nicerepr',
           '_boolean_icon',
           'nicerepr',
           'table']


BOOLEAN_MAPPING = {True: {'icon':'ui-icon-check','name':'yes'},
                   False: {'icon':'ui-icon-close','name':'no'}}


def _boolean_icon(val):
    v = BOOLEAN_MAPPING.get(val,'unknown')
    return '<span class="ui-icon %(icon)s" title="%(name)s">%(name)s</span>' % v


def nicerepr(val, nd = 3):
    if val is None:
        return sites.settings.DJPCMS_EMPTY_VALUE
    elif isinstance(val,datetime):
        time = val.time()
        if not time:
            return date_format(val.date(),sites.settings.DATE_FORMAT)
        else:
            return date_format(val,sites.settings.DATETIME_FORMAT)
    elif isinstance(val,date):
        return date_format(val,sites.settings.DATE_FORMAT)
    elif isinstance(val,bool):
        return _boolean_icon(val)
    else:
        try:
            return significant_format(val, n = nd)
        except TypeError:
            return val


def nice_items_id(items, id = None, nd = 3):
    return {'id': id,
            'display': (nicerepr(c,nd) for c in items)}


def table(headers, queryset_or_list, djp, model = None, nd = 3):
    '''Render a table'''
    if not model:
        try:
            model = queryset_or_list.model
        except AttributeError:
            pass
    cl = getattr(model,'mapper',None)
    if not cl:
        labels = headers
        items  = (nice_items_id(items,nd=nd) for items in queryset_or_list)
    else:
        labels = (cl.label_for_field(name) for name in headers)
        items  = (cl.result_for_item(headers, items, djp, nd) for items in queryset_or_list)
    
    return {'labels': labels,
            'items': items}


class BaseOrmWrapper(object):
    '''Base class for classes used to
wrap existing object relational mappers.

:parameter model: The ORM model class (for example a django model class).


.. attribute:: model

    The model class.

'''
    orm = None
    '''Object Relational Mapper name'''
    DoesNotExist = None
    '''Exception raise when an object is not available'''
    
    def __init__(self, model):
        self.model = model
        self.appmodel = None
        self.test()
        self.setup()
        self.hash = self._hash()
        sites.model_from_hash[self.hash] = model
        
    def setup(self):
        pass
    
    def test(self):
        raise NotImplementedError
    
    @classmethod
    def clear(cls):
        pass
    
    def __repr__(self):
        return str(self.model)
    __str__ = __repr__
    
    def _hash(self):
        raise NotImplementedError
    
    def pretty_repr(self, instance):
        '''Return a string with a pretty representation of instance'''
        return force_str(instance)
    
    def set_application(self, appmodel):
        self.appmodel = appmodel
        self.list_display = appmodel.list_display or []
        self.object_display = appmodel.object_display or self.list_display
        self.list_display_links = appmodel.list_display_links or []
        self.search_fields = appmodel.search_fields or []
        
    def getrepr(self, name, instance):
        attr = getattr(instance,name,None)
        if hasattr(attr,'__call__'):
            return attr()
        else:
            return attr
        
    def model_to_dict(self, instance, fields = None, exclude = None):
        raise NotImplementedError
    
    def _label_for_field(self, name):
        return name
        
    def appfuncname(self, name):
        return 'objectfunction__%s' % name
    
    def get_value(self, instance, name, default = nodata):
        default = default if default is not nodata else sites.settings.DJPCMS_EMPTY_VALUE
        func = getattr(self.appmodel,self.appfuncname(name),None)
        if func:
            return func(instance)
        else:
            return default
    
    def label_for_field(self, name):
        '''Get the lable for field or attribute or function *name*.'''
        try:
            return self._label_for_field(name)
        except:
            pass
        try:
            if self.appmodel:
                func = getattr(self.appmodel,self.appfuncname(name),None)
                if func:
                    return func(name)
                else:
                    return self.appmodel.get_label_for_field(name)
        except:
            return name
        
    def result_for_item(self, headers, result, djp, nd = 3):
        if isinstance(result, self.model):
            request = djp.request
            appmodel = request.site.for_model(self.model)
            if appmodel:
                list_display_links = appmodel.list_display_links
            else:
                list_display_links = []
            path  = djp.http.path_with_query(request)
            first = True
            id    = ('%s-%s') % (self.module_name,result.id)
            display = []
            item = {'id':id,'display':display}
            for field_name in headers:
                result_repr = self.getrepr(field_name, result, nd)
                if force_str(result_repr) == '':
                    result_repr = EMPTY_VALUE
                if (first and not list_display_links) or field_name in list_display_links:
                    first = False
                    if appmodel:
                        url = appmodel.viewurl(request, result, field_name)
                    else:
                        url = None
                else:
                    url = None
                
                var = result_repr
                if url:
                    if url != path:
                        var = '<a href="{0}" title="{1}">{1}</a>'.format(url, var)
                    else:
                        var = '<a>{0}</a>'.format(var)
                display.append(var)
            return item
        else:
            return nice_items_id(result, nd = nd)
        
    def getrepr(self, name, instance, nd = 3):
        '''representation of field *name* for *instance*.'''
        return nicerepr(self._getrepr(name,instance),nd)
    
    def _getrepr(self, name, instance):
        attr = getattr(instance,name,None)
        if hasattr(attr,'__call__'):
            attr = attr()
        if attr:
            return force_str(attr)
        else:
            return sites.settings.DJPCMS_EMPTY_VALUE
        
    def has_add_permission(self, user, obj=None):
        return user.is_superuser
    
    def has_change_permission(self, user, obj=None):
        return user.is_superuser
    
    def has_view_permission(self, user, obj = None):
        return True
    
    def has_delete_permission(self, user, obj=None):
        return user.is_superuser
    
    def get_object_id(self, obj):
        return '%s-%s' % (self.module_name,obj.id)
    
    def save(self, data, instance = None, commit = True):
        raise NotImplementedError

    @classmethod
    def setup_environment(cls):
        pass
