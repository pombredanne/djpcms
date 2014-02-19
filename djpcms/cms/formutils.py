'''Utility functions for :mod:`djpcms.forms`'''
import sys
import logging
from functools import partial
from datetime import datetime

from djpcms import forms, html, is_renderer, ajax
from djpcms.forms.layout import FormWidget
from djpcms.utils.text import to_string
from djpcms.utils.httpurl import urlsplit, QueryDict, iteritems
from djpcms.utils.dates import format
from djpcms.utils.async import is_async, is_failure

from .exceptions import HttpRedirect
from . import messages
from .submit import NEXT_KEY

logger = logging.getLogger('djpcms.forms')
Widget = html.Widget

form_actions = []


def apply_form_actions(form_widget):
    for form_action in form_actions:
        container = form_action(form_widget)
        if container is not None:
            form_widget = FormWidget(None, container, form=form_widget.form)
    return form_widget

def set_request_message(f, request):
    if '__all__' in f.errors:
        for msg in f.errors['__all__']:
            messages.error(request, msg)
    if '__all__' in f.messages:
        for msg in f.messages['__all__']:
            messages.info(request, msg)

def form_data_files(request, withdata=None, method='post', initial=None):
    '''
:parameter withdata: optional flag which can be used to avoid to bind
    the form to data in the event the request method is the same as the
    form action.
'''
    method = method.lower()
    rmethod = request.method.lower()
    get_data = request.GET
    if method == 'post':
        post = request.POST
        data = post.copy()
        # extend the dat with the GET dictionary, excluding the
        data.update(((k,v) for k,v in iteritems(get_data)\
                      if k is not NEXT_KEY and k not in post))
    else:
        data = get_data.copy()
    #data = request.POST if method == 'post' else request.GET
    bind_data = None
    if withdata or (withdata is None and rmethod == method):
        bind_data = data
    if bind_data is not None:
        return bind_data, request.FILES, initial
    else:
        if initial is None:
            initial = data
        else:
            initial.update(data)
        return None, None, initial

def request_get_data(request):
    data = request.GET
    if request.is_xhr or request.POST:
        ref = request.environ.get('HTTP_REFERER')
        parts = urlsplit(ref)
        extra_data = QueryDict(parts.query, request.encoding)
        extra_data.update(data)
        data = extra_data
    return data

def get_redirect(request, data=None, instance=None):
    '''Obtain the most suitable url to redirect the request.'''
    if instance is not None:
        req = request.for_model(instance=instance)
        if req:
            return req.url
    next = request.view.redirect_url(request)
    if not next and data:
        next = data.get(NEXT_KEY)
    return request.build_absolute_uri(next) if next else None

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

def get_form(request, form_factory, initial=None, prefix=None,
             withdata=None, instance=None, model=None, force_prefix=True,
             block=None, inputs=None, addinputs=None, **kw):
    '''Comprehensive method for building a :class:`djpcms.forms.HtmlForm`:

:parameter form_factory: A required instance of :class:`HtmlForm`.
:parameter initial: If not none, a dictionary of initial values.
:parameter prefix: Optional prefix string to use in the form.
:parameter addinputs: An optional function for creating inputs.
                      If available, it is called if the
                      available form class as no inputs associated with it.
                      Default ``None``.
'''
    method = form_factory.attrs['method']
    action = request.get_full_path()
    data, files, initial = form_data_files(request, withdata=withdata,
                                           method=method, initial=initial)
    submit_middleware = request.view.site.submit_data_middleware
    # Not binding data
    if data is None:
        inputs = forms.as_inputs(inputs) or form_factory.inputs
        if inputs is not None:
            inputs = [inp() for inp in inputs]
        elif addinputs:
            own_view = False if request.is_xhr else request.path==request.url
            inputs = form_inputs(instance, own_view)
        if inputs is None:
            inputs = []
        # Prefix
        if prefix is None and force_prefix:
            prefix = forms.generate_prefix()
            inputs.append(Widget('input:hidden', name=forms.PREFIX_KEY,
                                 value=prefix))
        # Add hidden inputs specified by the site
        for name, value in submit_middleware.extra_form_data(request):
            inputs.append(Widget('input:hidden', name=name, value=value))
        #referrer = request.environ.get('HTTP_REFERER')
    else:
        # Check the data
        inputs = None
        submit_middleware.check(request, data)
        if prefix is None:
            prefix = data.get(forms.PREFIX_KEY)
    # Create the form widget
    widget = form_factory(inputs=inputs, action=action, request=request,
                          initial=initial, instance=instance, model=model,
                          prefix=prefix, data=data, files=files, **kw)
    if not widget.form.is_bound:
        # The form is not bound, check for form action
        widget = apply_form_actions(widget)
    return widget

def return_form_errors(fhtml,request):
    if request.is_xhr:
        return fhtml.maker.json_messages(fhtml.form)
    else:
        return request.view.handle_response(request)

def submit_form(request, force_redirect=None, **kw):
    '''Comprehensive save method for forms.
This method try to deal with all possible events occurring after a form
has been submitted, including possible asynchronous behaviour.'''
    view = request.view
    if force_redirect is None:
        force_redirect = view.force_redirect
    fhtml = view.get_form(request, **kw)
    f = fhtml.form
    data = f.rawdata
    # The form has been aborted
    if forms.CANCEL_KEY in data:
        url = get_redirect(request, data, f.instance)
        raise HttpRedirect(url)
    # Save as new
    if forms.SAVE_AS_NEW_KEY in data and f.instance and f.instance.id:
        f.instance = view.mapper.save_as_new(f.instance, commit=False)
    # The form is valid. Invoke the submit_form method in the view
    if f.is_valid():
        editing = bool(f.instance and f.instance.id)
        response = view.submit_form(request, f)
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
    data = f.rawdata
    success_message = fhtml.success_message or view.success_message
    msg = success_message(request, response)
    f.add_message(msg)
    url = None
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
    elif force_redirect:
        url = get_redirect(request, data, response)

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
    if force_redirect:
        next = get_redirect(request, request.REQUEST)
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

def message_or_dialog(request, message):
    view = request.view
    if view.force_redirect or not request.is_xhr:
        if is_failure(message):
            messages.error(request, str(message))
        else:
            messages.info(request, message)
        raise HttpRedirect(request.url)
    title = 'Failure' if is_failure(message) else 'success'
    return ajax.dialog(request.environ,
                       hd=title,
                       bd=str(message),
                       modal=True)
