'''Utility functions for forms
'''
import sys
import logging
from datetime import datetime

from py2py3 import to_string

from djpcms import forms, http, html
from djpcms.core import messages
from djpcms.core.orms import mapper
from djpcms.utils import force_str, ajax
from djpcms.utils.urls import urlsplit
from djpcms.utils.dates import format

from .globals import *

logger = logging.getLogger('djpcms.forms')
Widget = html.Widget


def set_request_message(f, request):
    if '__all__' in f.errors:
        for msg in f.errors['__all__']:
            messages.error(request,msg)
    if '__all__' in f.messages:
        for msg in f.messages['__all__']:
            messages.info(request,msg)


def form_kwargs(request,
                withdata = False,
                method = 'post',
                inputs = None,
                initial = None,
                **kwargs):
    '''Form arguments aggregator.
Usage::

    form = MyForm(**form_kwargs(request))

:parameter withdata: if set to ``True`` force a bound form if data is
    available, otherwise it bound the form only if the request method is the
    same as the form method.
                     
    Default ``False``.
    
'''
    data = request.REQUEST
    if (withdata or request.method == method.lower()) and data:
        kwargs['data'] = data
        kwargs['files'] = request.FILES
    elif data:
        if initial is None:
            initial = data
        else:
            initial.update(data)
    kwargs['initial'] = initial
    kwargs['request'] = request
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
    return add_extra_fields(form,name,forms.CharField(\
                        widget=forms.HiddenInput, required = required))
    
    
def form_inputs(instance, own_view = False):
    '''Generate the submits elements to be added to the model form.
    '''
    if instance:
        sb = [Widget('input:submit', value = 'save', name = SAVE_KEY),
              Widget('input:submit', value = 'save as new', name = SAVE_AS_NEW_KEY)]
    else:
        sb = [Widget('input:submit', value = 'add', name = SAVE_KEY)]
        
    if own_view:
        sb.append(Widget('input:submit', value = 'save & continue',
                         name = SAVE_AND_CONTINUE_KEY))
        sb.append(Widget('input:submit', value = 'cancel',
                         name = CANCEL_KEY))
    return sb


def get_form(request,
             form_factory,
             initial = None,
             prefix = None,
             addinputs = None,
             withdata = False,
             instance = None,
             model = None,
             force_prefix = True):
    '''Comprehensive method for building a
:class:`djpcms.forms.HtmlForm` instance:

:parameter form_factory: A required instance of :class:`HtmlForm`.
:parameter initial: If not none, a dictionary of initial values.
:parameter prefix: Optional prefix string to use in the form.
:parameter addinputs: An optional function for creating inputs.
                      If available, it is called if the
                      available form class as no inputs associated with it.
                      Default ``None``.
'''
    referer = request.environ.get('HTTP_REFERER')
    data = request.REQUEST
    prefix = data.get(PREFIX_KEY,None)
    inputs = form_factory.inputs
    if inputs is not None:
        inputs = [inp.widget() for inp in inputs]
    elif addinputs:
        inputs = form_inputs(instance,  request.path == request.url)
    
    inputs = inputs or []
    inputs.append(Widget('input:hidden',name=REFERER_KEY,value=referer))
    if not prefix and force_prefix:
        prefix = generate_prefix()
        inputs.append(Widget('input:hidden',name=PREFIX_KEY,value=prefix))
                
    # Create the form instance
    form  = form_factory(inputs = inputs,
                         action = request.url,
                         **form_kwargs(request = request,
                                       initial = initial,
                                       instance = instance,
                                       model = model,
                                       prefix = prefix,
                                       withdata = withdata,
                                       method = form_factory.attrs['method']))
    
    if model:
        form.addClass(str(model._meta).replace('.','-'))
    return form


def return_form_errors(fhtml,request):
    if request.is_xhr:
        return fhtml.layout.json_messages(fhtml.form)
    else:
        return request.view.handle_response(request)
    

def request_get_data(request):
    if request.GET:
        return request.GET
    else:
        ref = request.environ.get('HTTP_REFERER')
        parts = urlsplit(ref)
        return http.QueryDict(parts.query,request.encoding)
    
    
def get_redirect(request, instance = None, force_redirect = False):
    '''Obtain the most suitable url to redirect the request to
according to the following algorithm:
 
* Check for ``next`` in the request environment query string
* Check for ``next`` in the environment referer query string
* If *force_redirect* is ``True``, calculate next from the
  :meth:`djpcms.views.djpcmsview.defaultredirect` passing both *request*
  and the optional *instance* parameter.
  
If none of the above works, it returns ``None``, otherwise it returns an
absolute url.
'''
    def _next():
        data = request_get_data(request)
        next = data.get('next')
        if next:
            return next
        elif force_redirect:
            return request.view.defaultredirect(request,instance=instance)
    return request.build_absolute_uri(_next())
    
    
def saveform(request, force_redirect = False):
    '''Comprehensive save method for forms.
This method try to deal with all possible events occurring after a form
has been submitted.'''
    view = request.view
    appmodel = view.appmodel
    is_ajax = request.is_xhr
    data = request.REQUEST
    curr = request.environ.get('HTTP_REFERER')
    referer = request.REQUEST.get(REFERER_KEY)
    fhtml = view.get_form(request)    
    layout = fhtml.layout
    f = fhtml.form
    instance = f.instance
    
    if CANCEL_KEY in data:
        redirect_url = get_redirect(request,instance,True)
        if is_ajax:
            return ajax.jredirect(url = redirect_url)
        else:
            return http.ResponseRedirect(redirect_url)
        
    if SAVE_AS_NEW_KEY in data and instance and instance.id:
        f.instance = instance = appmodel.mapper.save_as_new(instance,
                                                            commit = False)
        
    # The form is valid. Invoke the save method in the view
    if f.is_valid():
        editing = bool(instance and instance.id)
        instance = view.save(request,f)
        redirect_url = get_redirect(request,
                                    instance=instance,
                                    force_redirect=force_redirect)

        if ajax.isajax(instance):
            return instance
        elif instance == f:
            return layout.json_messages(f)
        msg = fhtml.success_message(instance,
                                    'changed' if editing else 'added')
        f.add_message(msg)
        
        # Save and continue. Redirect to referer if not AJAX or send messages 
        if SAVE_AND_CONTINUE_KEY in data:
            if editing:
                if is_ajax:
                    return layout.json_messages(f)
                else:
                    set_request_message(f,request)
                    return http.ResponseRedirect(curr)
            else:
                redirect_url = appmodel.changeurl(request, instance)
            
        # not forcing redirect. Check if we can send a JSON message
        if not force_redirect:
            if redirect_url == curr and is_ajax:
                return layout.json_messages(f)
            
        # We are Redirecting
        set_request_message(f,request)
        if is_ajax:
            return ajax.jredirect(url = redirect_url)
        else:
            return http.ResponseRedirect(redirect_url)
    else:
        if is_ajax:
            return layout.json_messages(f)
        else:
            return view.get_response(request)
        

def deleteinstance(request, force_redirect = True):
    '''Delete an instance from database'''
    instance = request.instance
    view = request.view
    next = get_redirect(request,force_redirect=force_redirect)
    bid = view.appmodel.remove_instance(instance)
    msg = 'Successfully deleted %s' % instance
    if request.is_xhr and bid and not force_redirect:
        return ajax.jremove('#%s' % bid)
    if next:
        messages.info(request,msg)
        if request.is_xhr:
            return ajax.jredirect(next)
        else:
            return http.ResponseRedirect(next)
    

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

