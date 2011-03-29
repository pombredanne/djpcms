from djpcms.utils import mark_safe

__all__ = ['htmldefaultdoc',
           'html_choices',
           'htmldoc']

htmldefaultdoc = 5


class HTMLdoc(object):
    
    def __init__(self, name, html, vimg, slash = "", meta = ""):
        self.name = name
        self._html = html
        self.vimg = vimg
        self.slash = slash
        self.meta = meta
        
    def __str__(self):
        return self.name
    
    @property
    def html(self):
        return mark_safe(self._html)
    
    def _validatorsrc(self, extra = ''):
        src = '#'
        if self.vimg:
            src= '''http://www.w3.org/Icons/%s%s.png''' % (self.vimg,extra)
        src = '''<img alt="Valid %s" src="%s"%s>''' % (self.name,src,self.slash)
        return mark_safe('''<a href="http://validator.w3.org/check?uri=referer">%s</a>''' % src)
    
    def bluevalidator(self):
        return self._validatorsrc('-blue')
    
    def validator(self):
        return self._validatorsrc()

def htmldoc(code = None):
    global _htmldict, htmldefaultdoc
    code = code or htmldefaultdoc
    if code in _htmldict:
        return _htmldict[code]
    else:
        return _htmldict[htmldefaultdoc]


htmldocs = (
            (1, 
             HTMLdoc('HTML 4.01',
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN
http://www.w3.org/TR/html4/strict.dtd">""",
                     "valid-html401")),
            (2, 
             HTMLdoc('HTML 4.01 Transitional',
    """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN
http://www.w3.org/TR/html4/loose.dtd">""",
                     "valid-html401")),
            (3, 
             HTMLdoc('XHTML 1.0 Strict',
                     """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">""",
                     "valid-xhtml10",
                     "/")),
            (4, 
             HTMLdoc('XHTML 1.0 Transitional',
    """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN
http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">""",
                     "valid-xhtml10",
                     "/",
                     meta = """<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<meta http-equiv="Content-Language" content="en-uk" />""")),
            (5, 
             HTMLdoc('HTML5',
                     """<!DOCTYPE html>\n<html>""",
                     None,
                     meta = '<meta charset="utf-8">')),
            )

_htmldict = dict(htmldocs)

html_choices = tuple(((t[0],t[1].name) for t in htmldocs))
