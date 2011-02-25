import sys
import logging
from datetime import datetime

from py2py3 import to_string

from djpcms import sites, forms
from djpcms.core import messages
from djpcms.core.orms import mapper
from djpcms.utils.translation import gettext as _
from djpcms.utils import force_str
from djpcms.utils.dates import format
from djpcms.utils.ajax import jredirect, jremove

from .html import HiddenInput
from .globals import generate_prefix

logger = logging.getLogger('djpcms.forms')

get_next = lambda request, name = "next" : request.POST.get(name,request.GET.get(name,None))


def next_and_current(request):
    next = get_next(request)
    curr = request.environ.get('HTTP_REFERER')
    if next:
        next = request.build_absolute_uri(next)
    return next,curr


def set_request_message(f, request):
    if '__all__' in f.errors:
        for msg in f.errors['__all__']:
            messages.error(request,msg)
    if '__all__' in f.messages:
        for msg in f.messages['__all__']:
            messages.info(request,msg)


def form_kwargs(request,
                instance = None,
                withdata = True,
                method = 'POST',
                own_view = True,
                inputs = None,
                **kwargs):
    '''Form arguments aggregator.
Usage::

    form = MyForm(**form_kwargs(request))

'''
    if request and withdata and request.method == method and own_view:
        data = dict(getattr(request,method).items())
        if inputs:
            bind = False
            for input in inputs:
                if input._attrs['name'] in data:
                    bind = True
        else:
            bind = True
        if bind:
            kwargs['data'] = data
            kwargs['files'] = request.FILES
    kwargs['request'] = request
    if instance:
        kwargs['instance'] = instance
    return kwargs


def add_extra_fields(form, name, field):
    '''form must be a form class, not an object
    '''
    fields = form.base_fields
    if name not in fields:
        fields[name] = field
    meta = getattr(form,'_meta',None)
    if meta:
        fields = meta.fields
        if fields and name not in fields:
            fields.append(name)
    return form


def add_hidden_field(form, name, required = False):
    return add_extra_fields(form,name,forms.CharField(widget=forms.HiddenInput, required = required))


def success_message(instance, mch):
    '''Very basic success message. Write your own for a better one.'''
    c = {'mch': mch}
    if instance:
        c['name'] = mapper(instance).pretty_repr(instance)
        return '{0[name]} succesfully {0[mch]}'.format(c)
    else:
        return '0[mch]'.format(c)


def update_initial(request, form_class, initial = None,
                   own_view = True):    
    if request.method == 'GET':
        params = dict(request.GET.items())
        next   = params.get('next',None)
        if not next and not own_view:
            next = request.path
        if next:
            form_class = add_hidden_field(form_class,'next')
        initial = initial or {}
        initial['next'] = next
    return initial


def get_form(djp,
             form_factory,
             method = 'POST',
             initial = None,
             prefix = None,
             addinputs = None,
             withdata = True,
             instance  = None,
             model = None,
             form_withrequest = None,
             template = None,
             form_ajax = False,
             withinputs = True,
             force_prefix = False):
    '''Comprehensive method for building a
:class:`djpcms.forms.HtmlForm` instance:
    
:parameter djp: instance of :class:`djpcms.views.DjpResponse`.
:parameter form_factory: A required instance of :class:`djpcms.forms.HtmlForm`.
:parameter method: optional string indicating submit method. Default ``POST``.
:parameter initial: If not none, a dictionary of initial values.
:parameter prefix: Optional prefix string to use in the form.
:parameter addinputs: An optional function for creating inputs.
                      If available, it is called if the
                      available form class as no inputs associated with it.
                      Default ``None``.
'''
    request  = djp.request
    own_view = djp.own_view()
    data = request.data_dict
    prefix = data.get('__prefixed__',None)
    save_as_new = data.has_key('_save_as_new')
    submits = form_factory.submits
    if submits:
        inputs = [forms.SubmitInput(value = val, name = nam) for val,nam in submits]
    elif addinputs:
        inputs = addinputs(instance, own_view)
    else:
        inputs = []
        
    if not prefix and force_prefix:
        prefix = generate_prefix()
        pinput = forms.HiddenInput(name='__prefixed__',value=prefix)
        inputs.append(pinput)
                
    # Create the form instance
    form  = form_factory(**form_kwargs(request     = request,
                                       initial     = initial,
                                       instance    = instance,
                                       prefix      = prefix,
                                       withdata    = withdata,
                                       method      = method,
                                       own_view    = own_view))
    
    # Get the form HTML Widget
    widget = form_factory.widget(form,
                                 inputs = inputs,
                                 action = djp.url,
                                 method = method.lower())
    
    if form_ajax:
        widget.addClass(djp.css.ajax)
    if model:
        widget.addClass(str(model._meta).replace('.','-'))
    return widget

    
def saveform(djp, editing = False, force_redirect = False):
    '''Comprehensive save method for forms.
This method try to deal with all possible events occurring after a form
has been submitted.'''
    view = djp.view
    request = djp.request
    http = djp.http
    is_ajax = request.is_xhr
    POST = request.POST
    GET = request.GET
    curr = request.environ.get('HTTP_REFERER')
    next = get_next(request)
    fhtml = view.get_form(djp)
    
    layout = fhtml.layout
    f = fhtml.form
    
    if POST.has_key("_cancel"):
        redirect_url = next
        if not redirect_url:
            if djp.instance:
                redirect_url = view.appmodel.viewurl(request,djp.instance)
            if not redirect_url:
                redirect_url = view.appmodel.searchurl(request) or '/'

        if is_ajax:
            return jredirect(url = redirect_url)
        else:
            return http.HttpResponseRedirect(redirect_url)
    
    # The form is valid. Invoke the save method in the view
    if f.is_valid():
        editing  = editing if not POST.has_key('_save_as_new') else False
        instance = view.save(request, f)
        smsg     = getattr(view,'success_message',success_message)
        msg      = smsg(instance, 'changed' if editing else 'added')
        f.add_message(msg)
        
        # Save and continue. Redirect to referer if not AJAX or send messages 
        if POST.has_key('_save_and_continue'):
            if is_ajax:
                return layout.json_messages(f)
            else:
                set_request_message(f,request)
                return http.HttpResponseRedirect(curr)

        # Check redirect url
        redirect_url = view.defaultredirect(request,
                                            next = next,
                                            instance = instance)
            
        # not forcing redirect. Check if we can send a JSON message
        if not force_redirect:
            if redirect_url == curr and is_ajax:
                return layout.json_messages(f)
            
        # We are Redirecting
        set_request_message(f,request)
        if is_ajax:
            return jredirect(url = redirect_url)
        else:
            return http.HttpResponseRedirect(redirect_url)
    else:
        if is_ajax:
            return layout.json_messages(f)
        else:
            return view.handle_response(djp)
        

def deleteinstance(djp, force_redirect = False):
    '''Delete an instance from database'''
    instance = djp.instance
    view    = djp.view
    request = djp.request
    
    curr    = request.environ.get('HTTP_REFERER')
    next    = get_next(request)
    if next:
        next = request.build_absolute_uri(next)
    next = next or curr
        
    bid     = view.appmodel.remove_object(instance)
    msg     = 'Successfully deleted %s' % instance
    if request.is_ajax():
        if next == curr and bid and not force_redirect:
            return jremove('#%s' % bid)
        else:
            messages.info(request,msg)
            return jredirect(next)
    else:
        messages.info(request,msg)
        next = next or curr
        return http.HttpResponseRedirect(next)
    
    

def fill_form_data(f):
    '''Utility for filling a dictionary with data contained in a form'''
    data = {}
    initial = f.initial
    is_bound = f.is_bound
    for field in f:
        v = field.data
        if v is None and not is_bound:
             v = getattr(field.field,'initial',None)
             if v is None:
                 v = initial.get(field.name,None)
        if v is not None:
            data[field.html_name] = v
    return data 

