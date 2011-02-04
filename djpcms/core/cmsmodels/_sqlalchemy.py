import sqlalchemy as sql
from sqlalchemy import orm, Column
from sqlalchemy.ext.declarative import declarative_base

from djpcms.core.page import PageInterface, BlockInterface,\
                             TemplateInterface, MarkupMixin

from py2py3 import UnicodeMixin

Model = declarative_base()


class TimeStamp(Model):
    last_modified = Column(sql.DATETIME)
    created = Column(sql.DATETIME)
    

class Site(Model,UnicodeMixin):
    domain = Column(sql.String(300), unique = True)
    name = Column(sql.String(200), unique = True)
        
    def __str__(self):
        return self.name
    
    
class InnerTemplate(TimeStamp,TemplateInterface):
    '''Page Inner template'''
    name     = Column(sql.String(200))
    template = Column(sql.Text())
    blocks   = Column(sql.Text())
    
    
class Page(TimeStamp, PageInterface):
    '''The page model holds several information regarding pages in the sitemap.'''
    site        = field.ForeignKey(Site, required = False)
    application_view = field.SymbolField(required = False)
    redirect_to = field.ForeignKey('self',
                                   required  = False,
                                   related_name = 'redirected_from')
    title       = Column(sql.String(60))
    url_pattern = Column(sql.String(200))
    link        = field.CharField()
    inner_template = field.ForeignKey(InnerTemplate, required = False)
    template    = field.CharField()
    in_navigation = field.IntegerField(default=1)
    cssinfo     = field.ForeignKey(CssPageInfo, required = False)
    is_published = field.BooleanField(default=True)
    # Access
    requires_login = field.BooleanField(default = False)
    soft_root = field.BooleanField(default=False)
    parent    = field.ForeignKey('self',
                                  required = False,
                                  related_name = 'children')
    doctype = field.IntegerField(default = htmltype.htmldefault)
    insitemap = field.BooleanField(default = True)
    
    # Denormalized level in the tree and url, for performance 
    level       = field.IntegerField(default = 0)
    url         = field.SymbolField()
    application = field.SymbolField(required = False)
    user        = field.SymbolField(required = False)
    

    
    