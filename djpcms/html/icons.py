'''Utility functions for jQuery icons
'''

def jqueryicon(url,text,icon_class, title=''):
    '''Render an anchor with classes for displaying a jQuery icon'''
    if not url:
        return ''
    title = title or text
    return '<a class="icon {0}" href="{1}" title="{2}">{3}</a>'.format(icon_class,url,title,text)


def makeicon(ext):
    return lambda url,text='',title='' : jqueryicon(url,text,'ui-icon-'+ext,title=title)


circle_plus = makeicon('circle-plus')
circle_minus = makeicon('circle-minus')
pencil = makeicon('pencil') # for editing links