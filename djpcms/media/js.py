JQUERY_PATH = 'https://ajax.googleapis.com/ajax/libs/jquery/{0}/jquery.min.js'
JQUERY_UI_PATH = 'https://ajax.googleapis.com/ajax/libs/jqueryui/\
{0}/jquery-ui.min.js'
SWFOBJECT_PATH = 'https://ajax.googleapis.com/ajax/libs/swfobject/\
{0}/swfobject.js'
JQUERY_TEMPLATE = 'http://ajax.aspnetcdn.com/ajax/jquery.templates/beta1/\
jquery.tmpl.min.js'
HIGHLIGHTS = 'http://yandex.st/highlightjs/6.1/highlight.min.js'
RAPHAEL = 'http://cdnjs.cloudflare.com/ajax/libs/raphael/2.1.0/raphael-min.js'


BOOSTRAP_TWIPSY = 'http://twitter.github.com/bootstrap/1.4.0/bootstrap-twipsy.js'
BOOSTRAP_TWIPSY = 'http://twitter.github.com/bootstrap/1.4.0/bootstrap-twipsy.js'


def bootstrap(settings):
    v = settings.BOOTSTRAP_VERSION
    libs = settings.BOOTSTRAP_LIBS
    if libs:
        base = 'http://twitter.github.com/bootstrap/{0}/'.format(v)
        return tuple((base+'bootstrap-{0}.js'.format(lib) for lib in libs))
    else:
        return ()

def jquery_path(settings):
    v = settings.JQUERY_VERSION
    if v:
        return JQUERY_PATH.format(v)


def jquery_ui_path(settings):
    v = settings.JQUERY_UI_VERSION
    if v:
        return JQUERY_UI_PATH.format(v)
    
    
def jquery_paths(settings):
    jq = jquery_path(settings)
    if jq:
        return jq,jquery_ui_path(settings)
    return jq,None


def swfobject_path(settings):
    v = settings.SWFOBJECT_VERSION
    if v:
        return SWFOBJECT_PATH.format(v)


def jquerytemplate(settings = None):
    return JQUERY_TEMPLATE