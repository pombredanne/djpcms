from datetime import date, datetime

from django.utils.dateformat import format as date_format, time_format

from djpcms.conf import settings
from djpcms.utils import mark_safe
from djpcms.template import loader 

BOOLEAN_MAPPING = {True: ('ui-icon-check','yes'), False: ('ui-icon-close','no')}
EMPTY_VALUE = settings.DJPCMS_EMPTY_VALUE


def _boolean_icon(val):
    v = BOOLEAN_MAPPING.get(val,'unknown')
    return mark_safe(u'<span class="ui-icon %s" alt="%s" />' % v)


def nicerepr(val):
    if isinstance(val,datetime):
        time = val.time()
        if not time:
            return date_format(val.date(),settings.DATE_FORMAT)
        else:
            return date_format(val,settings.DATETIME_FORMAT)
    elif isinstance(val,date):
        return date_format(val,settings.DATE_FORMAT)
    elif isinstance(val,bool):
        return _boolean_icon(val)
    else:  
        return val
        

class ModelTypeWrapper(object):
    
    def __init__(self, appmodel):
        self.list_display = appmodel.list_display
        self.object_display = appmodel.object_display or self.list_display
        self.list_display_links = appmodel.list_display_links or []
        self.search_fields = appmodel.search_fields or []
        self.test(appmodel.model)
        self.appmodel = appmodel
        self.model = appmodel.model
        self.setup()
        
    def test(self, model):
        raise NotImplementedError
    
    def _label_for_field(self, name):
        return name
        
    def appfuncname(self, name):
        return 'extrafunction__%s' % name
    
    def get_value(self, instance, name, default = EMPTY_VALUE):
        func = getattr(self.appmodel,self.appfuncname(name),None)
        if func:
            return func(self.request, instance)
        else:
            return default
    
    def label_for_field(self, name):
        '''Get the lable for field or attribute or function *name*.'''
        try:
            return self._label_for_field(name)
        except:
            if self.appmodel:
                func = getattr(self.appmodel,self.appfuncname(name),None)
                if func:
                    return name
            raise AttributeError("Attribute %s not available" % name)
        
    def getrepr(self, name, instance):
        '''representation of field *name* for *instance*.'''
        return nicerepr(self._getrepr(name,instance))
    
    def _getrepr(self, name, instance):
        raise NotImplementedError
    
    def url_for_result(self, request, instance):
        if self.appmodel:
            return self.appmodel.viewurl(request, instance)
        else:
            return None
        
    def has_add_permission(self, user, obj=None):
        return user.is_superuser
    
    def has_change_permission(self, user, obj=None):
        return user.is_superuser
    
    def has_view_permission(self, user, obj = None):
        return True
    
    def has_delete_permission(self, user, obj=None):
        return user.is_superuser
    
    def totable(self, obj):
        label_for_field = self.label_for_field
        getrepr = self.getrepr
        def data():
            for field in self.object_display:
                name = label_for_field(field)
                yield {'name':name,'value':getrepr(name,obj)}
        return loader.render_to_string(['%s/%s_table.html' % (self.app_label,self.module_name),
                                        'djpcms/components/object_definition.html'],
                                        {'data':data(),
                                         'item':obj})
            
        