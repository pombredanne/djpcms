
class ajaxhtml(object):
    
    def __new__(cls):
        obj = super(ajaxhtml,cls).__new__(cls)
        d = {}
        obj._dict = d
        
        # AJAX classes
        d['post_view_key']           = 'xhr'
        d['ajax']                    = 'ajax'
        d['errorlist']               = 'errorlist'
        d['formmessages']            = 'form-messages'
        d['field_separator']         = 'field-separator'
        
        # css decorators
        d['autocomplete_class']       = 'djp-autocomplete'
        d['multi_autocomplete_class'] = 'multi'
        d['calendar_class']           = 'dateinput'
        d['currency_input']           = 'currency-input'
        d['edit']                     = 'editable'
        d['delete']                   = 'deletable'
        d['secondary_in_list']        = 'secondary'
        d['nicebutton']               = 'nice-button'
        d['main_nav']                 = 'main-nav'      # Main navigation class
        
        # classes for links
        d['link_active'] = 'ui-state-active'
        d['link_default'] = '' # 'ui-state-default'
        
        return obj
    
    def __init__(self):
        d = self._dict
        for k,v in d.items():
            setattr(self,k,v)
    
    def __setitem__(self, k, v):
        self._dict[k] = v

    @property
    def tojson(self):
        from djpcms.template import json_dump_safe
        return json_dump_safe(self._dict)
    
