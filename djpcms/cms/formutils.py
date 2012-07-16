'''Utility functions for :mod:`djpcms.forms`'''
import sys
import logging
from functools import partial
from datetime import datetime

from djpcms import forms, html, is_renderer
from djpcms.utils.text import to_string
from djpcms.utils.httpurl import urlsplit, QueryDict
from djpcms.utils.dates import format
from djpcms.utils.async import is_async

from .exceptions import HttpRedirect
from . import messages

logger = logging.getLogger('djpcms.forms')
Widget = html.Widget


def set_request_message(f, request):
    if '__all__' in f.errors:
        for msg in f.errors['__all__']:
            messages.error(request, msg)
    if '__all__' in f.messages:
        for msg in f.messages['__all__']:
            messages.info(request, msg)

def form_kwargs(request, withdata=None, method='post', inputs=None,
                initial=None, **kwargs):
    '''Form arguments aggregator.
Usage::

    form = MyForm(**form_kwargs(request))

:parameter withdata: Force the form to have or not have bound data.
    If not supplied, the form is bound to data only if the request
    method is the same as the form method.
    
    Default ``None``.
    
:parameter method: Form method.
                     
    Default ``"post"``.
'''
    data = request.REQUEST
    if (withdata or (withdata is None and request.method == method.lower()))\
        and data:
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
        sb = [Widget('input:submit', value='save', name=forms.SAVE_KEY),
              Widget('input:submit', value='save as new',
                     name=forms.SAVE_AS_NEW_KEY)]
    else:
        sb = [Widget('input:submit', value='add', name=forms.SAVE_KEY)]
        
    if own_view:
        sb.append(Widget('input:submit', value = 'save & continue',
                         name=forms.SAVE_AND_CONTINUE_KEY))
        sb.append(Widget('input:submit', value='cancel', name=forms.CANCEL_KEY))
    return sb

def get_form(request,
             form_factory,
             initial=None,
             prefix=None,
             addinputs=None,
             withdata=None,
             instance=None,
             model=None,
             force_prefix=True):
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
    referrer = request.environ.get('HTTP_REFERER')
    data = request.REQUEST
    prefix = data.get(forms.PREFIX_KEY, None)
    inputs = form_factory.inputs
    if inputs is not None:
        inputs = [inp() for inp in inputs]
    elif addinputs:
        if not request.is_xhr:
            own_view = request.path==request.url
        else:
            own_view = False
        inputs = form_inputs(instance, own_view)
    
    inputs = inputs if inputs is not None else []
    inputs.append(Widget('input:hidden', name=forms.REFERER_KEY,
                         value=referrer))
    if prefix is None and force_prefix:
        prefix = forms.generate_prefix()
        inputs.append(Widget('input:hidden',
                             name=forms.PREFIX_KEY,
                             value=prefix))
    # Create the form widget
    return form_factory(inputs=inputs,
                        action=request.url,
                        **form_kwargs(request=request,
                                      initial=initial,
                                      instance=instance,
                                      model=model,
                                      prefix=prefix,
                                      withdata=withdata,
                                      method=form_factory.attrs['method']))

def return_form_errors(fhtml,request):
    if request.is_xhr:
        return fhtml.maker.json_messages(fhtml.form)
    else:
        return request.view.handle_response(request)
    
def request_get_data(request):
    data = request.GET
    if request.is_xhr or request.POST:
        ref = request.environ.get('HTTP_REFERER')
        parts = urlsplit(ref)
        extra_data = QueryDict(parts.query, request.encoding)
        extra_data.update(data)
        data = extra_data
    return data
    
def get_redirect(request, instance = None, force_redirect = False):
    '''Obtain the most suitable url to redirect the request to
according to the following algorithm:
 
* Check for ``next`` in the request environment query string
* Check for ``next`` in the environment referrer query string
* If *force_redirect* is ``True``, calculate next from the
  :meth:`djpcms.views.djpcmsview.redirect_url` passing both *request*
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
            return request.view.redirect_url(request,instance=instance)
    n = _next()
    return request.build_absolute_uri(n) if n else None
    
def saveform(request, force_redirect=None):
    '''Comprehensive save method for forms.
This method try to deal with all possible events occurring after a form
has been submitted, including possible asynchronous behavior.'''
    view = request.view
    if force_redirect is None:
        force_redirect = view.force_redirect
    data = request.REQUEST
    curr = request.environ.get('HTTP_REFERER')
    referrer = data.get(forms.REFERER_KEY)
    fhtml = view.get_form(request)
    f = fhtml.form
    
    if forms.CANCEL_KEY in data:
        url = get_redirect(request, f.instance, True)
        raise HttpRedirect(url)
        
    if forms.SAVE_AS_NEW_KEY in data and f.instance and f.instance.id:
        f.instance = view.mapper.save_as_new(f.instance, commit=False)
        
    # The form is valid. Invoke the save method in the view
    if f.is_valid():
        editing = bool(f.instance and f.instance.id)
        response = view.save(request, f)
        if is_async(response):
            return response.add_callback(partial(_finish, request, editing,
                                                 fhtml, force_redirect))
        else:
            return _finish(request, editing, fhtml, force_redirect, response)
    else:
        if request.is_xhr:
            return fhtml.maker.json_messages(f)
        else:
            return view.get_response(request)
        
def _finish(request, editing, fhtml, force_redirect, response):
    view = request.view
    f = fhtml.form
    if is_renderer(response):
        return response
    elif response == f:
        return fhtml.maker.json_messages(f)
    data = request.REQUEST
    msg = fhtml.success_message(request, response,
                                'changed' if editing else 'added')
    f.add_message(msg)
    
    # Save and continue. Redirect to referrer if not AJAX or send messages 
    if forms.SAVE_AND_CONTINUE_KEY in data:
        if editing:
            if request.is_xhr:
                return fhtml.maker.json_messages(f)
            else:
                #editing and continuing to edit
                curr = request.environ.get('HTTP_REFERER')
                set_request_message(f,request)
                raise HttpRedirect(curr)
        else:
            url = view.redirect_url(request, response, 'change')
    else:
        url = get_redirect(request,
                           instance=response,
                           force_redirect=force_redirect)
    
    if not url:
        if request.is_xhr:
            return fhtml.maker.json_messages(f)
        else:
            set_request_message(f,request)
            return view.get_response(request)
    else:
        set_request_message(f, request)
        raise HttpRedirect(url)

def deleteinstance(request, force_redirect=None):
    '''Delete an instance from database'''
    instance = request.instance
    view = request.view
    if force_redirect is None:
        force_redirect = view.force_redirect
    next = get_redirect(request,force_redirect=force_redirect)
    bid = view.appmodel.remove_instance(instance)
    msg = 'Successfully deleted %s' % instance
    if request.is_xhr and bid and not force_redirect:
        return ajax.jremove('#%s' % bid)
    if next:
        messages.info(request,msg)
        raise HttpRedirect(next)
    
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

