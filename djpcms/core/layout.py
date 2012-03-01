from djpcms import UnicodeMixin
from djpcms.html import Widget, WidgetMaker

__all__ = ['Meta','html_choices',
           'htmldoc','htmldefaultdoc']


htmldefaultdoc = 5

_Meta = WidgetMaker(tag='meta',
                    inline=True,
                    attributes=('content', 'http-equiv', 'name', 'charset'))

def Meta(*args,**kwargs):
    return Widget(_Meta,*args,**kwargs)


class HTMLdoc(UnicodeMixin):
    
    def __init__(self, typ, name, html, vimg = None, slash = ""):
        self.typ = typ
        self.name = name
        self.html = html
        self.vimg = vimg
        self.slash = slash
        
    def __unicode__(self):
        return self.name
    
    def meta(self, name, value):
        if value:
            if name == 'charset':
                if self.typ == 5:
                    return Meta(charset = value)
                else:
                    return Meta(content = 'text/html; charset='+value)\
                                .attr('http-equiv','content-type')
            else:
                return Meta(name = name, content = value)
                        

htmldocs = (
            (1, 
             HTMLdoc(1,'HTML 4.01',
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN
http://www.w3.org/TR/html4/strict.dtd">""",
                     "valid-html401")),
            (2, 
             HTMLdoc(2,'HTML 4.01 Transitional',
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN
http://www.w3.org/TR/html4/loose.dtd">""",
                     "valid-html401")),
            (3, 
             HTMLdoc(3,'XHTML 1.0 Strict',
                     """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">""",
                     "valid-xhtml10",
                     "/")),
            (4, 
             HTMLdoc(4,'XHTML 1.0 Transitional',
    """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN
http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">""",
             "valid-xhtml10",
             "/",
             )),
            (5, 
             HTMLdoc(5,'HTML5',
                     """<!DOCTYPE html>\n<html>"""),
            )
            )


_htmldict = dict(((h[0],h[1]) for h in htmldocs))

html_choices = tuple(((t[0],t[1].name) for t in htmldocs))


def htmldoc(code = None):
    global _htmldict, htmldefaultdoc
    code = code or htmldefaultdoc
    if code in _htmldict:
        return _htmldict[code]
    else:
        return _htmldict[htmldefaultdoc]

