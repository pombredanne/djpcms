import os
import json

from .base import handle, BaseTemplateHandler, TemplateHandler

# Default Implementation
loader = TemplateHandler()

# Default Implementation
#mark_safe = loader.mark_safe
json_dump_safe = lambda data: loader.mark_safe(json.dumps(data))


def make_default_inners():
    '''Default inner templates are located in the djpcms/templates/djpcms/inner directory'''
    from djpcms import DJPCMS_DIR
    from djpcms.models import InnerTemplate
    from djpcms.core.orms import mapper
    if not InnerTemplete:
        return
    inner_dir = os.path.join(DJPCMS_DIR,'templates','djpcms','inner')
    load = loader.load_template_source
    mp = mapper(InnerTemplate)
    added = []
    for d in os.listdir(inner_dir):
        if os.path.isfile(os.path.join(inner_dir,d)):
            t,l = load('djpcms/inner/'+d)
            name = d.split('.')[0]
            try:
                mp.get(name = name)
            except mp.DoesNotExist:
                it = InnerTemplate(name = name, template = t)
                it.save()
                added.append(it.name)
    return added
