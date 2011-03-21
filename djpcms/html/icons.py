'''Utility functions for jQuery icons
'''
from djpcms.utils.const import EMPTY
from djpcms.utils import mark_safe


button_class = ' class="button"'
simple_class = ' class="simple-icon"'

def wrap_state(cn, func):
    return lambda *args, **kwargs: mark_safe('<span class="{0}">{1}</span>'.\
                                             format(cn,func(*args,**kwargs))) 

def jqueryicon(url,text,icon_class = None, title='', button = True):
    '''Render an anchor with classes for displaying a jQuery icon'''
    if not url:
        if icon_class:
            return mark_safe('<span class="ui-icon ui-icon-{0}"></span>'.format(icon_class))
        else:
            return ''
    title = title or text
    cl = button_class if button else EMPTY
    if icon_class:
        if not cl:
            cl = simple_class
            rel = '<span class="ui-icon ui-icon-{0}"></span>'.format(icon_class)
            text = '<span class="text">{0}</span>'.format(text)
        else:
            rel = '<span class="ui-icon-{0}"></span>'.format(icon_class)
    else:
        rel = EMPTY
    return mark_safe('<a{0} href="{1}" title="{2}">{3}{4}</a>'.format(cl,url,title,rel,text))


def makeicon(icon_class, cn = None):
    return lambda url = None,text='',title='',button=True : \
            jqueryicon(url,text,icon_class,title=title,button=button)
      

circle_plus = makeicon('circle-plus')
circle_minus = makeicon('circle-minus')
circle_close = makeicon('circle-close')
circle_check = makeicon('circle-check')
pencil = makeicon('pencil') # for editing links
yes = makeicon('circle-check')
no = makeicon('circle-close')
#no = wrap_state('ui-state-error',makeicon('circle-close'))

