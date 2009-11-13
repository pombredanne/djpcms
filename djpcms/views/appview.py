import copy

from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, RequestContext

from djpcms.models import AppPage
from djpcms.utils.html import Paginator
from djpcms.views.baseview import djpcmsview
from djpcms.views.site import get_view_from_url


class AppView(djpcmsview):
    '''
    Base class for application views
    '''
    creation_counter = 0
    page_model       = AppPage
    
    def __init__(self, url = None, parent = None, name = None, isapp = True, template_name = None, in_navigation = True):
        self.args     = None
        self.urlbit   = url or u''
        self.parent   = parent
        self.name     = name
        self.curl     = ''
        self.isapp    = isapp
        self.func     = None
        self.appmodel = None
        self.code     = None
        self.editurl  = None
        self.in_navigation = in_navigation
        if template_name:
            self.template_name = template_name
        # Increase the creation counter, and save our local copy.
        self.creation_counter = AppView.creation_counter
        AppView.creation_counter += 1
        
    def __unicode__(self):
        return u'%s: %s' % (self.name,self.rurl)
    
    def __get_rurl(self):
        return r'^%s$' % self.curl
    rurl = property(fget = __get_rurl)
    
    def __get_model(self):
        return self.appmodel.model
    model = property(fget = __get_model)
    
    def edit_rurl(self, edit):
        return r'^%s/%s$' % (edit,self.curl)
    
    def handle_reponse_arguments(self, request, *args, **kwargs):
        view = copy.copy(self)
        view.args = args
        return view
    
    def get_prefix(self, data):
        '''
        Get form prefix from data.
        '''
        for k,v in data.items():
            sv = str(v)
            if sv and k.endswith('-prefix'):
                return sv
    
    def processurlbits(self, appmodel):
        '''
        Process urlbit to create the clean url resolver self.curl
        and the url parser self.purl
        '''
        self.appmodel = appmodel
        if self.parent:
            baseurl = self.parent.curl
            purl    = self.parent.purl
            nargs   = self.parent.nargs
        else:
            baseurl = self.appmodel.baseurl[1:]
            purl    = self.appmodel.baseurl
            nargs   = 0
        
        if self.urlbit:
            bits = self.urlbit.split('/')
            for bit in bits:
                if bit:
                    if bit.startswith('('):
                        purl  += '%s/'
                        nargs += 1
                    else:
                        purl += '%s/' % bit
            self.curl = '%s%s/' % (baseurl,self.urlbit)
        else:
            self.curl = baseurl
                        
        self.purl  = purl
        self.nargs = nargs
        
    def get_url(self, *args):
        '''
        get application url
        '''
        args = self.args or args
        if self.nargs:
            return self.purl % args[:self.nargs]
        else:
            return self.purl
    
    def parentview(self, request):
        '''
        Retrive the parent view
        '''
        if not self.parent:
            # No parent check for flat pages
            return get_view_from_url(request,self.appmodel.parent_url)
        else:
            return self.parent
    
    def get_page(self):
        if self.code:
            try:
                return self.page_model.objects.get_for_code(self.code)
            except:
                if self.parent:
                    return self.parent.get_page()
                else:
                    return None
        else:
            return None
        
    def render(self, request, prefix, wrapper, *args):
        '''
        Render the application child.
        This method is reimplemented by subclasses.
        By default it renders the search application
        '''
        pass
    
    def inner_content(self, request):
        return self.render(request,None,None)
    
    def __deepcopy__(self, memo):
        result = copy.copy(self)
        return result
    
    
class ObjectView(AppView):
    '''
    Application view for objects
    '''
    def __init__(self, url = None, parent = None,
                name = None, isapp = True, **kwargs):
        self.object = None
        super(ObjectView,self).__init__(url = url, parent = parent,
                                        name = name, isapp = isapp, **kwargs)
        
    def handle_reponse_arguments(self, request, *args, **kwargs):
        try:
            return self(self.appmodel.get_object(*args,**kwargs))
        except ObjectDoesNotExist, e:
            raise http.Http404(str(e))
    
    def get_url(self, *args):
        '''
        get object application url
        '''
        if self.object:
            return self.purl % self.appmodel.objectbits(self.object)
        else:
            return self.purl % args
    
    def title(self, request, pagetitle):
        try:
            return pagetitle % self.object
        except:
            return pagetitle
    
    def __call__(self, obj):
        view = copy.copy(self)
        view.object = obj
        return view
    

class SearchApp(AppView):
    '''
    Base class for searching objects in model
    '''
    def __init__(self, *args, **kwargs):
        super(SearchApp,self).__init__(*args,**kwargs)
    
    def handle_reponse_arguments(self, request, *args, **kwargs):
        view = copy.copy(self)
        view.args   = args
        view.kwargs = kwargs
        return view
    
    def basequery(self, request):
        return self.appmodel.basequery(request)
    
    def myquery(self, query, request, *args, **kwargs):
        return query
    
    def get_item_template(self, obj):
        opts = obj._meta
        template_name_0 = '%s_search_item.html' % opts.module_name
        template_name_1 = '%s/%s' % (opts.app_label,template_name_0)
        return [template_name_0,template_name_1]
    
    def render(self, request, prefix, wrapper, *args):
        '''
        Render the application child.
        '''
        args     = self.args or args
        #url      = self.get_url(*args)
        url = '.'
        query    = self.basequery(request)
        if query:
            query = self.myquery(query, request, *args, **self.kwargs)
        f  = self.appmodel.get_searchform(request, prefix, wrapper, url)
        p  = Paginator(request, query)
        return loader.render_to_string(['content/pagination.html',
                                        'djpcms/content/pagination.html'],
                                        {'form':f,
                                         'paginator': p,
                                         'data': self.data_generator(request, prefix, wrapper, p.qs)})
    
    def data_generator(self, request, prefix, wrapper, data):
        app = self.appmodel
        for obj in data:
            content = app.object_content(request, prefix, wrapper, obj)
            content.update({'item': obj,
                            'editurl': app.editurl(request, obj),
                            'viewurl': app.viewurl(request, obj),
                            'deleteurl': app.deleteurl(request, obj)})
            yield loader.render_to_string(template_name    = self.get_item_template(obj),
                                          context_instance = RequestContext(request, content))

class ArchiveApp(SearchApp):
    '''
    Search view with archive subviews
    '''
    def __init__(self, *args, **kwargs):
        super(ArchiveApp,self).__init__(*args,**kwargs)
    
    def _date_code(self):
        return self.appmodel.date_code
    
    def myquery(self, query, request, year = None, month = None, day = None):
        '''
        Override myquery for handling year, month and day
        '''
        if year:
            date_code = self._date_code()
            kwargs = {'%s__year' % date_code: int(year)}
            if month:
                kwargs['%s__month' % date_code] = int(month)
                if day:
                    kwargs['%s__day' % date_code] = int(day)
            query = query.filter(**kwargs)
        return query