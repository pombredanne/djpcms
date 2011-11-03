from djpcms import UnicodeMixin
from djpcms.html import icons 


class AppList(UnicodeMixin):
    
    def __init__(self, app, djp):
        self.app = app
        self.djp = djp
        
    def __iter__(self):
        djp = self.djp
        request = djp.request
        site = djp.site
        appmodel = self.app.appmodel
        for app in site._nameregistry.values():
            if app is appmodel:
                continue
            view = app.root_view
            vdjp = view(djp.request)
            url = vdjp.url
            if url:
                name = nicename(app.name)
                addurl = icons.circle_plus(app.addurl(request))
                yield ('<a href="{0}">{1}</a>'.format(url,name),addurl)

    def __unicode__(self):
        '''Render an object as definition list.'''
        data = self._data()
        obj = self.obj
        mapper = self.appmodel.mapper
        content = {'module_name':mapper.module_name,
                   'id':mapper.get_object_id(obj),
                   'data':data,
                   'item':obj}
        return self.djp.render(('%s/%s_definition.html' % (mapper.app_label,mapper.module_name),
                                OBJECT_DEF_TEMPLATE),
                                content)
        
