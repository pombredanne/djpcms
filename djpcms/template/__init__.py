import os
import json
from .base import handle, BaseTemplateHandler, TemplateHandler

loader = TemplateHandler()

# Default Implementation
mark_safe = loader.mark_safe
escape = loader.escape
conditional_escape = loader.conditional_escape
#Template = loader.template_class
#Context = loader.context_class
#RequestContext = loader.request_context
json_dump_safe = lambda data: loader.mark_safe(json.dumps(data))



def make_default_inners():
    '''Default inner templates are located in the djpcms/templates/djpcms/inner directory'''
    from djpcms import DJPCMS_DIR
    from djpcms.models import InnerTemplate
    inner_dir = os.path.join(DJPCMS_DIR,'templates','djpcms','inner')
    load = loader.load_template_source
    for d in os.listdir(inner_dir):
        if os.path.isfile(os.path.join(inner_dir,d)):
            t,l = load('djpcms/inner/'+d)
            name = d.split('.')[0]
            it = InnerTemplate(name = name, template = t)
            it.save()
