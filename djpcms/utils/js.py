JQUERY_PATH = 'https://ajax.googleapis.com/ajax/libs/jquery/{0}/jquery.min.js'
JQUERY_UI_PATH = 'https://ajax.googleapis.com/ajax/libs/jqueryui/\
{0}/jquery-ui.min.js'
SWFOBJECT_PATH = 'https://ajax.googleapis.com/ajax/libs/swfobject/\
{0}/swfobject.js'
JQUERY_TEMPLATE = 'http://ajax.aspnetcdn.com/ajax/jquery.templates/beta1/\
jquery.tmpl.min.js'


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