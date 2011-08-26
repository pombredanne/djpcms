import json
from djpcms.utils import mark_safe

class Html(object):        
    # AJAX classes
    post_view_key           = 'xhr'
    ajax                    = 'ajax'
    errorlist               = 'errorlist'
    formmessages            = 'form-messages'
        
    multi_autocomplete_class = 'multi'
    calendar_class           = 'dateinput'
    currency_input           = 'currency-input'
    edit                     = 'editable'
    delete                   = 'deletable'
    secondary_in_list        = 'secondary'
    main_nav                 = 'main-nav'
    objectdef = 'object-definition'
        
    # classes for links
    link_active = 'ui-state-active'
    link_default = '' # 'ui-state-default'
    
    def __init__(self):
        for key,v in Html.__dict__.items():
            if isinstance(v,str):
                setattr(self,key,v)
        self.tojson = mark_safe(json.dumps(self.__dict__))
