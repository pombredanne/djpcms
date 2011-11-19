import os
import json

from djpcms import DJPCMS_DIR
from .base import *


json_dump_safe = lambda data: loader.mark_safe(json.dumps(data))


def make_default_inners(sites):
    '''Default inner templates are located in the djpcms/templates/djpcms/inner
 directory'''
    from djpcms.core import orms
    Page = sites.Page
    if not Page:
        raise ValueError('No cms models defined. Cannot create iner templates')
    template = sites.all()[0].template
    template_model = Page.template_model
    mp = orms.mapper(template_model)
    inner_dirs = [(os.path.join(DJPCMS_DIR,'templates','djpcms','inner'),
                   'djpcms/inner/')]
    for dir in sites.settings.TEMPLATE_DIRS:
        inner_dir = os.path.join(dir,'inner')
        if os.path.isdir(inner_dir):
            inner_dirs.append((inner_dir,'inner/'))
    load = template.load_template_source
    added = []
    for inner_dir, relpath in inner_dirs:
        for d in os.listdir(inner_dir):
            if os.path.isfile(os.path.join(inner_dir,d)):
                t,l = load(relpath+d)
                name = d.split('.')[0]
                try:
                    mp.get(name = name)
                except mp.DoesNotExist:
                    it = template_model(name = name, template = t)
                    it.save()
                    added.append(it.name)
    return added
