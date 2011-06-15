import os
import json

from .base import handle, BaseTemplateHandler, TemplateHandler

# Default Implementation
loader = TemplateHandler()

json_dump_safe = lambda data: loader.mark_safe(json.dumps(data))


def make_default_inners():
    '''Default inner templates are located in the djpcms/templates/djpcms/inner directory'''
    from djpcms import DJPCMS_DIR, sites
    from djpcms.models import InnerTemplate
    from djpcms.core.orms import mapper
    if not InnerTemplate:
        return
    inner_dirs = [(os.path.join(DJPCMS_DIR,'templates','djpcms','inner'),'djpcms/inner/')]
    for dir in sites.settings.TEMPLATE_DIRS:
        inner_dir = os.path.join(dir,'inner')
        if os.path.isdir(inner_dir):
            inner_dirs.append((inner_dir,'inner/'))
    load = loader.load_template_source
    mp = mapper(InnerTemplate)
    added = []
    for inner_dir, relpath in inner_dirs:
        for d in os.listdir(inner_dir):
            if os.path.isfile(os.path.join(inner_dir,d)):
                t,l = load(relpath+d)
                name = d.split('.')[0]
                try:
                    mp.get(name = name)
                except mp.DoesNotExist:
                    it = InnerTemplate(name = name, template = t)
                    it.save()
                    added.append(it.name)
    return added
