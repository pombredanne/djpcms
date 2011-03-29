from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

from djpcms.views import appview, appsite
from djpcms.html import Paginator
from djpcms.apps.included.tagging import ArchiveTaggedApplication, TagApplication

from flowrepo.models import FlowRelated, FlowItem, Report
from flowrepo.models import Message, Category, Image, Attachment

from .forms import *


class FlowMainView(appview.SearchView):
    pass


def addContentModel(self, djp, **kwargs):
    try:
        djp.kwargs['content_model'] = self.appmodel.get_content_model(kwargs['content'])
    except:
        raise http.Http404
    

def get_content_url(self, djp, **kwargs):
    addContentModel(self,djp,**kwargs)
    return super(self.__class__,self).get_url(djp, **kwargs)
    

class ContentView(appview.SearchView):
        
    def get_url(self, djp, **kwargs):
        return get_content_url(self, djp, **kwargs)
        
    def title(self, page, content_model = None, **kwargs):
        if content_model:
            return force_unicode(content_model._meta.verbose_name_plural)
        else:
            return super(ContentView,self).title(page,**kwargs)
        
    def appquery(self, djp):
        qs = super(ContentView,self).appquery(djp)
        content_model = djp.getdata('content_model')
        if content_model:
            ctype = ContentType.objects.get_for_model(content_model)
            return qs.filter(content_type = ctype)
        else:
            return self.model.objects.none()
        

class FlowAddView(appview.AddView):
    
    def get_url(self, djp, **kwargs):
        return get_content_url(self, djp, **kwargs)
    
    def title(self, page, content_model = None, **kwargs):
        t = self.appmodel.add_title.get(content_model,None)
        if not t:
            return super(FlowAddView,self).title(page, content = None, **kwargs)
        else:
            return t
        

class FlowEditView(appview.ChangeView):
    
    def get_url(self, djp, **kwargs):
        url = super(FlowEditView,self).get_url(djp, **kwargs)
        djp.kwargs['content_model'] = djp.instance.object.__class__
        return url    

       
slug_regex = '(?P<id>[-\.\w]+)'
class FlowItemApplication(ArchiveTaggedApplication):
    '''Mighty Flow Application!'''
    date_code        = 'timestamp'
    form_withrequest = True
    form             = FlowForm
    search_fields    = ['name','description']
    form_ajax        = False
    split_days       = True
    inherit          = True
    insitemap        = True
    content_names    = {Report:'writing'} # dictionary for mapping a model into a name used for url
    content_forms    = {Report: NiceReportForm,
                        Image: NiceUloaderForm,
                        Attachment: NiceUloaderForm}
    form_templates   = {Report: 'flowrepo/report-form.html'}
    add_title        = {Report: 'write', Image: 'upload'}
    
    main             = FlowMainView()
    search           = appview.SearchView(regex = 'search', parent = 'main', in_navigation = 0)
    autocomplete     = appview.AutocompleteView(display = 'name', parent = 'main')
    upload_file      = appview.AddView(regex = 'upload', form = NiceUloaderForm, parent = 'main')
    applications     = ContentView(regex = '(?P<content>[-\w]+)', parent = 'main')
    add              = FlowAddView(parent = 'applications')
    view             = appview.ViewView(regex = slug_regex, parent = 'applications')
    edit             = FlowEditView()
    delete           = appview.DeleteView()
        
    def __init__(self, *args, **kwargs):
        content_models = {}
        self.content_names  = kwargs.pop('content_names',self.content_names)
        for cn,model in FlowItem.objects.models_by_name.items():
            cname = self.content_names.get(model,cn)
            self.content_names[model] = cname
            content_models[cname] = model
        self.content_models = content_models
        super(FlowItemApplication,self).__init__(*args, **kwargs)
        
    def get_content_model(self, content):
        if isinstance(content,basestring):
            model = self.content_models.get(content,None)
            return self.model.objects.models_by_name.get(model.__name__.lower(), None)
        else:
            return content
        
    def form_template(self, djp):
        content = self.get_content_model(djp.kwargs.get('content',None))
        return self.form_templates.get(content,None)
        
    def get_form(self, djp, form_class, **kwargs):
        content = djp.getdata('content_model')
        if not form_class:
            form_class = self.content_forms.get(content,form_class)
        uni = super(FlowItemApplication,self).get_form(djp,form_class,forceform=True,**kwargs)
        if content:
            uni.addClass(str(content._meta).replace('.','-'))
        return uni
        
    def objptr(self, object):
        try:
            return object.object
        except:
            return object
    
    def flowitem(self, object):
        try:
            return object.flowitem()
        except:
            return None

    def modelsearch(self):
        return FlowItem
            
    def basequery(self, djp):
        user = djp.request.user
        return FlowItem.objects.public(user = user, model = self.model)
    
    def get_search_fields(self):
        if self.search_fields:
            return self.search_fields
        else:
            from django.contrib.admin import site
            admin = site._registry.get(FlowItem,None)
            if admin:
                return admin.search_fields

    def has_permission(self, request = None, obj=None):
        '''
        evaluate only if obj is an instance of flowitem
        '''
        obj = self.flowitem(obj)
        if not obj:
            return True
        if not request:
            return obj.can_user_view()
        else:
            return obj.can_user_view(request.user)
    
    def has_edit_permission(self, request = None, obj=None):
        obj = self.flowitem(obj)
        if super(FlowItemApplication,self).has_edit_permission(request, obj):
            if obj:
                return request.user in obj.authors.all()
            else:
                return True
        else:
            return False
        
    def get_object_view_template(self, obj, wrapper):
        item = self.flowitem(obj)
        obj  = item.object
        opts = obj._meta
        template_name = '%s.html' % opts.module_name
        return ['%s/%s' % (opts.app_label,template_name),
                'djpcms/components/object.html']
        
    def get_item_template(self, obj, wrapper):
        model = self.objptr(obj)._meta.module_name
        return ['components/%s_list_item.html' % model,
                'flowrepo/%s_list_item.html' % model,
                'flowrepo/flowitem_list_item.html']
    
    def title_object(self, obj):
        object = self.objptr(obj)
        name = getattr(object,'name',None)
        if not name:
            return str(obj)
        else:
            return name
        
    def object_content(self, djp, obj):
        '''
        Utility function for getting more content out of an instance of a model
        '''
        c = super(FlowItemApplication,self).object_content(djp,obj)
        c['authors']  = obj.niceauthors()
        c['external'] = True
        return c
    
    def objectbits(self, instance):
        '''
        Get arguments from model instance used to construct url
        By default it is the object id
        @param obj: instance of self.model
        @return: dictionary of url bits 
        '''
        obj = instance.object
        if not obj:
            instance.delete()
            return None
        rep = {'content':self.content_names[obj.__class__]}
        if hasattr(obj,'slug'):
            rep['id'] = obj.slug
        else:
            rep['id'] = obj.id
        return rep
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        try:
            model = self.get_content_model(kwargs['content'])
            if model:
                id   = kwargs.get('id',None)
                try:
                    obj = model.objects.get(slug = id)
                except:
                    try:
                        obj = model.objects.get(id = int(id))
                    except:
                        return None
            return FlowItem.objects.get_from_instance(obj)
        except:
            return None



class WebAccountApplication(TagApplication):
    list_display_links = ('name',)
    search_fields = ('name','url','tags')
    name             = 'webaccount'
    form             = NiceWebAccountForm
    form_withrequest = True
    inherit          = True
    
    add       = appview.AddView()
    view      = appview.ViewView()
    edit      = appview.ChangeView()
    delete    = appview.DeleteView()
        
    def has_permission(self, request = None, obj = None):
        if not request:
            return False
        try:
            return request.user.id == getattr(self.settings,'FOR_USER_ID',None)
        except:
            False
    
    def permissionDenied(self, djp):
        raise djp.http.Http404('bad link')
    