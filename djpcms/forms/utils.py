import sys
import logging
from datetime import datetime

from py2py3 import to_string

from djpcms import sites, forms, http, html
from djpcms.core import messages
from djpcms.core.orms import mapper
from djpcms.utils.translation import gettext as _
from djpcms.utils import force_str, ajax
from djpcms.utils.dates import format

from .globals import *

logger = logging.getLogger('djpcms.forms')



def set_request_message(f, request):
    if '__all__' in f.errors:
        for msg in f.errors['__all__']:
            messages.error(request,msg)
    if '__all__' in f.messages:
        for msg in f.messages['__all__']:
            messages.info(request,msg)


def form_kwargs(request,
                withdata = True,
                method = 'POST',
                own_view = True,
                inputs = None,
                initial = None,
                **kwargs):
    '''Form arguments aggregator.
Usage::

    form = MyForm(**form_kwargs(request))

'''
    #if request and withdata and request.method == method and own_view:
    data = getattr(request,request.method)
    if request.method == method and data:
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
    return add_extra_fields(form,name,forms.CharField(widget=forms.HiddenInput, required = required))


def success_message(instance, mch):
    '''Very basic success message. Write your own for a better one.'''
    c = {'mch': mch}
    if instance:
        c['name'] = mapper(instance).pretty_repr(instance)
        return '{0[name]} succesfully {0[mch]}'.format(c)
    else:
        return '0[mch]'.format(c)


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
             force_prefix = True):
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
    request = djp.request
    referer = request.environ.get('HTTP_REFERER')
    own_view = djp.own_view()
    data = request.REQUEST
    prefix = data.get(PREFIX_KEY,None)
    
    save_as_new = SAVE_AS_NEW_KEY in data
    inputs = form_factory.inputs
    if not inputs and addinputs:
        inputs = addinputs(instance, own_view)
        
    if not prefix and force_prefix:
        prefix = generate_prefix()
        pinput = html.Widget('input:hidden',name=PREFIX_KEY,value=prefix)
        inputs.append(pinput)
        
    pinput = html.Widget('input:hidden',name=REFERER_KEY,value=referer)
    inputs.append(pinput)
                
    # Create the form instance
    form  = form_factory(inputs = inputs,
                         **form_kwargs(request = request,
                                       initial = initial,
                                       instance = instance,
                                       model = model,
                                       prefix = prefix,
                                       withdata = withdata,
                                       method = method,
                                       own_view = own_view))\
            .addAttr('action',djp.url)\
            .addAttr('method',method.lower())
    
    if form_ajax:
        form.addClass(djp.css.ajax)
    if model:
        form.addClass(str(model._meta).replace('.','-'))
    return form


def return_form_errors(fhtml,djp):
    if djp.request.is_xhr:
        return fhtml.layout.json_messages(fhtml.form)
    else:
        return djp.view.handle_response(djp)
    
    
def saveform(djp, editing = False, force_redirect = False):
    '''Comprehensive save method for forms.
This method try to deal with all possible events occurring after a form
has been submitted.'''
    view = djp.view
    appmodel = view.appmodel
    request = djp.request
    is_ajax = request.is_xhr
    data = request.REQUEST
    curr = request.environ.get('HTTP_REFERER')
    referer = data.get(REFERER_KEY,None)
    fhtml = view.get_form(djp)
    
    layout = fhtml.layout
    f = fhtml.form
    
    if CANCEL_KEY in data:
        redirect_url = referer
        if not redirect_url:
            if djp.instance:
                redirect_url = appmodel.viewurl(request,djp.instance)
            if not redirect_url:
                redirect_url = appmodel.searchurl(request) or '/'

        if is_ajax:
            return ajax.jredirect(url = redirect_url)
        else:
            return http.ResponseRedirect(redirect_url)
    
    # The form is valid. Invoke the save method in the view
    if f.is_valid():
        editing  = editing if not SAVE_AS_NEW_KEY in data else False
        if editing:
            instance = view.save(djp,f)
        else:
            instance = view.save_as_new(djp,f)
        if ajax.isajax(instance):
            return instance
        elif instance == f:
            return layout.json_messages(f)
        smsg     = getattr(view,'success_message',success_message)
        msg      = smsg(instance, 'changed' if editing else 'added')
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

        # Check redirect url
        else:
            redirect_url = view.defaultredirect(request,
                                                #next = referer,
                                                instance = instance)
            
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
            return view.handle_response(djp)
        

def deleteinstance(djp, force_redirect = True):
    '''Delete an instance from database'''
    instance = djp.instance
    view    = djp.view
    request = djp.request
    #next = request.environ.get('HTTP_REFERER')
    bid = view.appmodel.remove_object(instance)
    msg = 'Successfully deleted %s' % instance
    if request.is_xhr and bid and not force_redirect:
        return ajax.jremove('#%s' % bid)
    
    messages.info(request,msg)
    root_url = view.appmodel.root_view(djp, **djp.kwargs).url
    if request.is_xhr:
        return ajax.jredirect(root_url)
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

