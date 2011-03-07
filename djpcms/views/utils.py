from djpcms import UnicodeMixin
from djpcms.template import loader

OBJECT_DEF_TEMPLATE = 'djpcms/object_definition.html'

class ObjectDefinition(UnicodeMixin):
    
    def __init__(self, appmodel, djp):
        self.appmodel = appmodel
        self.djp = djp
        self.obj = djp.instance
        
    def _data(self):
        obj = self.obj
        mapper = self.appmodel.mapper
        label_for_field = mapper.label_for_field
        getrepr = mapper.getrepr
        for field in self.appmodel.object_display:
            name = label_for_field(field)
            yield {'name':name,
                   'value':getrepr(field,obj)}
                
    def __unicode__(self):
        '''Render an object as definition list.'''
        data = self._data()
        obj = self.obj
        mapper = self.appmodel.mapper
        content = {'module_name':mapper.module_name,
                   'id':mapper.get_object_id(obj),
                   'data':data,
                   'item':obj}
        return loader.render(('%s/%s_definition.html' % (mapper.app_label,mapper.module_name),
                              OBJECT_DEF_TEMPLATE),
                              content)
        