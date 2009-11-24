import copy

from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, RequestContext
from django.utils.dates import MONTHS_3_REV

from djpcms.models import Page
from djpcms.utils.html import Paginator
from djpcms.views.baseview import djpcmsview
from djpcms.views.site import get_view_from_url
from djpcms.utils.func import force_number_insert
from djpcms.utils.ajax import jremove, dialog
from djpcms.utils import form_kwargs


class AppView(djpcmsview):
    '''
    Base class for application views
    '''
    creation_counter = 0
    
    def __init__(self,
                 regex     = None,
                 parent    = None,
                 name      = None,
                 isapp     = True,
                 isplugin  = False,
                 template_name = None,
                 in_navigation = False):
        # number of positional arguments in the url
        self.num_args = 0
        self.urlbit   = regex or u''
        self.parent   = parent
        self.name     = name
        self._regex   = ''
        self.isapp    = isapp
        self.isplugin = isplugin
        self.func     = None
        self.appmodel = None
        self.code     = None
        self.editurl  = None
        self.in_nav   = in_navigation
        if template_name:
            self.template_name = template_name
        # Increase the creation counter, and save our local copy.
        self.creation_counter = AppView.creation_counter
        AppView.creation_counter += 1
        
    def __unicode__(self):
        return u'%s: %s' % (self.name,self.regex)
    
    def __get_regex(self):
        return '^%s$' % self._regex
    regex = property(fget = __get_regex)
    
    def __get_model(self):
        return self.appmodel.model
    model = property(fget = __get_model)
    
    def in_navigation(self, request, page):
        if self.in_nav:
            if page:
                return page.in_navigation
            else:
                return 1
        else:
            return 0
    
    def linkname(self, page, **urlargs):
        if not page:
            return self.appmodel.name
        else:
            return page.link
        
    def title(self, page, **urlargs):
        if not page:
            return self.appmodel.name
        else:
            return page.title
    
    def edit_regex(self, edit):
        return r'^%s/%s$' % (edit,self._regex)
    
    def processurlbits(self, appmodel):
        '''
        Process url bits and store information for navigation and urls
        '''
        self.appmodel = appmodel
        self.ajax     = appmodel.ajax
        if self.parent:
            baseurl = self.parent._regex
            purl    = self.parent.purl
            nargs   = self.parent.num_args
        else:
            baseurl = self.appmodel.baseurl[1:]
            purl    = self.appmodel.baseurl
            nargs   = 0
        
        breadcrumbs = []
        if self.urlbit:
            bits = self.urlbit.split('/')
            for bit in bits:
                if bit:
                    if bit.startswith('('):
                        st = bit.find('<') + 1
                        en = bit.find('>')
                        if st and en:
                            name = bit[st:en]
                        else:
                            nargs += 1
                            name   = 'arg_no_key_%s' % nargs
                            
                        name  = '%(' + name + ')s'
                        purl += name + '/'
                        breadcrumbs.append(name)
                    else:
                        breadcrumbs.append(bit)
                        purl += '%s/' % bit
            self._regex = '%s%s/' % (baseurl,self.urlbit)
        else:
            self._regex = baseurl
        
        self.breadcrumbs = breadcrumbs
        self.purl     = purl
        self.num_args = nargs
        
    def content_dict(self, cl):
        return copy.copy(cl.urlargs)
        
    def get_url(self, request, **kwargs):
        '''
        get application url
        '''
        if kwargs:
            return self.purl % kwargs
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
                return Page.objects.get_for_application(self.code)
            except:
                if self.parent:
                    return self.parent.get_page()
    
    def basequery(self, request, **kwargs):
        '''
        Base query for application
        If this is the root view (no parents) it returns the default
        basequery
        '''
        if self.parent:
            return self.parent.appquery(request)
        else:
            return self.appmodel.basequery(request)
    
    def appquery(self, request, *args, **kwargs):
        '''
        This function implements the application query.
        By default return the input basequery (usually all items of a model)
        @param request: HttpRequest
        @param *args: Extra positional arguments coming from the database
        @param *kwargs: Extra key-valued arguments coming from the database
        @return: a queryset
        '''
        return self.basequery(request)
    
    def render(self, djp, **kwargs):
        '''
        Render the application child.
        This method is reimplemented by subclasses.
        By default it renders the search application
        '''
        pass
    
    def children(self, request, instance = None, **kwargs):
        views = []
        for view in self.appmodel.applications.values():
            if view is self or not view.has_permission(request, instance):
                continue
            djp = view.requestview(request, **kwargs)
            nav = djp.in_navigation()
            if nav:
                views.append(djp)
        return self.sortviewlist(views)
    
    def get_prefix(self, djp):
        return None
        data = dict(djp.request.POST.items())
        for k,v in data.items():
            sv = str(v)
            if sv and k.endswith('-prefix'):
                return sv
    
    def has_permission(self, request = None, obj = None):
        '''
        Delegate to appmodel
        '''
        return self.appmodel.has_permission(request, obj)
    
    def permissionDenied(self, djp):
        return self.appmodel.permissionDenied(djp)
    
    def __deepcopy__(self, memo):
        return copy.copy(self)


class SearchView(AppView):
    '''
    Base class for searching objects in model
    '''
    def __init__(self, *args, **kwargs):
        super(SearchView,self).__init__(*args,**kwargs)
    
    def render(self, djp, **kwargs):
        '''
        Perform the custom query over the model objects and return a paginated result
        @param request: HttpRequest
        @param prefix: prefix for forms
        @param wrapper: html wrapper object
        @see: djpcms.utils.html.pagination for pagination
        '''
        request = djp.request
        if kwargs:
            urlargs = djp.urlargs
            urlargs.update(kwargs)
            djp = self.requestview(request, *urlargs)
        query = self.appquery(request, *djp.args, **djp.kwargs)
        f  = self.appmodel.get_searchform(djp)
        p  = Paginator(request, query)
        c  = self.content_dict(djp)
        c.update({'form':f,
                  'paginator': p,
                  'items': self.appmodel.data_generator(djp, p.qs)})
        return loader.render_to_string(['components/pagination.html',
                                        'djpcms/components/pagination.html'],
                                        c)


class ArchiveView(SearchView):
    '''
    Search view with archive subviews
    '''
    def __init__(self, *args, **kwargs):
        super(ArchiveView,self).__init__(*args,**kwargs)
    
    def _date_code(self):
        return self.appmodel.date_code
    
    def content_dict(self, djp):
        c = super(ArchiveView,self).content_dict(djp)
        month = c.get('month',None)
        if month:
            try:
                c['month'] = int(month)
            except:
                c['month'] = MONTHS_3_REV.get(month,None)
        year = c.get('year',None)
        day  = c.get('day',None)
        if year:
            c['year'] = int(year)
        if day:
            c['day'] = int(day)
        return c
    
    def appquery(self, request, year = None, month = None, day = None, **kwargs):
        dt       = self._date_code()
        dateargs = {}
        if year:
            dateargs['%s__year' % dt] = int(year)
        
        if month:
            try:
                month = int(month)
            except:
                month = MONTHS_3_REV.get(str(month),None)
            if month:
                dateargs['%s__month' % dt] = month
    
        if day:
            dateargs['%s__day' % dt] = int(day)
            
        qs = self.basequery(request, **kwargs)
        if dateargs:
            return qs.filter(**dateargs)
        else:
            return qs 
        
        

class AddView(AppView):
    '''
    Standard Add method
    '''
    def __init__(self, regex = 'add', parent = None,
                 name = 'add', isplugin = True, **kwargs):
        '''
        Set some default values for add application
        '''
        super(AddView,self).__init__(regex  = regex,
                                     parent = parent,
                                     name   = name,
                                     isplugin = isplugin,
                                     **kwargs)
    
    def has_permission(self, request = None, obj = None):
        return self.appmodel.has_add_permission(request, obj)
    
    def get_form(self, djp):
        return self.appmodel.get_form(djp)
    
    def save(self, f):
        return self.appmodel.object_from_form(f)
    
    def render(self, djp):
        '''
        Render the add view
        '''
        f = self.get_form(djp)
        return f.render()
    
    def default_ajax_view(self, djp):
        djp.prefix = self.get_prefix(djp)
        f = self.get_form(djp)
        if f.is_valid():
            try:
                instance = self.save(f)
            except Exception, e:
                return f.errorpost('%s' % e)
            return f.messagepost('%s added' % instance)
        else:
            return f.jerrors
        
        
# Application views which requires an object
class ObjectView(AppView):
    '''
    Application view for objects.
    A view of this type has an embedded object available.
    URL is generated by the object
    '''
    def __init__(self, *args, **kwargs):
        super(ObjectView,self).__init__(*args, **kwargs)
    
    def get_url(self, djp, instance = None, **urlargs):
        '''
        get object application url
        If instance not defined it return None
        '''
        if instance:
            return self.purl % self.appmodel.objectbits(instance)
        else:
            instance = self.appmodel.get_object(**urlargs)
            if instance:
                url = self.purl % urlargs
                djp.instance = instance
                return url
    
    def title(self, request, pagetitle):
        try:
            return pagetitle % self.object
        except:
            return pagetitle
    

# View and object
class ViewView(ObjectView):
    
    def __init__(self, regex = '(\d+)', parent = None, name = 'view', **kwargs):
        '''
        By default the relative url is given by the databse id number
        '''
        super(ViewView,self).__init__(regex = regex, parent = parent,
                                      name = name, **kwargs)
        
    def render(self, djp):
        '''
        Render the add view
        '''
        return self.appmodel.render_object(djp)
    
    
# Delete an object. POST method only. not GET method should modify databse
class DeleteView(ObjectView):
    _methods      = ('post',) 
    
    def __init__(self, regex = 'delete', parent = 'view', name = 'delete',
                 isapp = False, **kwargs):
        super(DeleteView,self).__init__(regex = regex, parent = parent,
                                        name = name, isapp = isapp,
                                        **kwargs)
        
    def has_permission(self, request = None, obj = None):
        return self.appmodel.has_delete_permission(request, obj)
    
    def default_ajax_view(self, djp):
        instance = djp.instance
        try:
            bid = self.appmodel.remove_object(instance)
            if bid:
                return jremove('#%s' % bid)
            else:
                pass
        except:
            raise ValueError('Could not remove %s' % instance)
      

# Edit/Change an object
class EditView(ObjectView):
    '''
    Edit view
    '''
    def __init__(self, regex = 'edit', parent = 'view', name = 'edit',  **kwargs):
        super(EditView,self).__init__(regex = regex, parent = parent, name = name, **kwargs)
    
    def has_permission(self, request = None, obj = None):
        return self.appmodel.has_edit_permission(request, obj)
    
    def get_form(self, djp):
        return self.appmodel.get_form(djp)
    
    def render(self, djp):
        f = self.get_form(djp)
        return f.render()
    
    def save(self, f):
        return self.appmodel.object_from_form(f)
    
    def default_ajax_view(self, djp):
        djp.prefix = self.get_prefix(djp)
        f = self.get_form(djp)
        if f.is_valid():
            try:
                instance = self.save(f)
            except Exception, e:
                return f.errorpost('%s' % e)
            return f.messagepost('%s modified' % instance)
        else:
            return f.jerrors
