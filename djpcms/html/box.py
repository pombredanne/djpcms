from .base import Widget, WidgetMaker


__all__ = ['box']
    

BoxHeader = WidgetMaker(tag='div', default_class='hd', key='hd')\
                        .add(WidgetMaker(tag='h2'),
                             WidgetMaker(tag='div', default_class='edit-menu',
                                         key='menu'))

Box = WidgetMaker(tag = 'div', default_class='djpcms-html-box')\
                        .add(BoxHeader,
                             WidgetMaker(tag='div', default_class='bd'),
                             WidgetMaker(tag='div', default_class='ft'))

BoxNoFooter = WidgetMaker(tag = 'div', default_class='djpcms-html-box')\
                        .add(BoxHeader,
                             WidgetMaker(tag='div', default_class='bd'))


def box(hd=None, bd=None, ft=None, minimize=False,
        collapsable=False, collapsed=False, delurl=None, **kwargs):
    '''Create a box :class:`Widget`.'''
    if ft:
        b = Box((hd,bd,ft), **kwargs)
    else:
        b = BoxNoFooter((hd,bd), **kwargs)
    cn = 'ui-icon-circle-triangle-n'
    if collapsed:
        cn = 'ui-icon-circle-triangle-s'
        b.addClass('collapsed')
        collapsable = True
    menu = []
    if collapsable:
        b.addClass('collapsable')
        menu.append('<a class="collapse" href="#">'\
                    '<span class="ui-icon {0}"></span></a>'.format(cn))
    if delurl:
        menu.append('<a class="ajax" href="{0}">'\
                    '<span class="ui-icon ui-icon-closethick">'\
                    '</span></a>'.format(delurl))
    if menu:
        b['hd']['menu'].add(menu)
    return b

