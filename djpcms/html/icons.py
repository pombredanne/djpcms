
def jqueryicon(url,icon_class):
    if not url:
        return ''
    return '<a class="icon {0}"></a>'.format(icon_class)


def makeicon(ext):
    return lambda url : jqueryicon(url,'ui-icon-'+ext)

circle_plus = makeicon('circle-plus')