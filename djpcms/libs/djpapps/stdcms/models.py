from datetime import datetime

from stdnet import orm

from djpcms.core.page import PageInterface, BlockInterface,\
                             TemplateInterface, MarkupMixin,\
                             BlockContentManager
from djpcms import html


ModelBase = orm.StdModel
field = orm

app_label = 'djpcms'


def create_new_content(user = None, **kwargs):
    user_last = None
    if user and user.is_authenticated():
        user_last = user
    ct = SiteContent(user_last = user_last, **kwargs)
    ct.save()
    return ct


additional_where = ((1, 'head'),
                    (2, 'body javascript'))


class TimeStamp(ModelBase):
    '''Timestamp abstract model class.'''
    last_modified     = field.DateTimeField()
    '''Python datetime instance when ``self`` was last modified.'''
    created           = field.DateTimeField(default = datetime.now)
    '''Python datetime instance when ``self`` was created.'''
    
    class Meta:
        abstract = True
        
    def save(self, commit = True):
        self.last_modified = datetime.now()
        if commit:
            return super(TimeStamp,self).save()
        else:
            return super(TimeStamp,self)
    

class InnerTemplate(TimeStamp,TemplateInterface):
    '''Page Inner template'''
    name     = field.SymbolField()
    template = field.CharField()
    blocks   = field.CharField()
        
    def __unicode__(self):
        return self.name
    
    def save(self, commit = True):
        self.blocks_from_content()
        if commit:
            return super(InnerTemplate,self).save()
        else:
            return super(InnerTemplate,self)
    
    class Meta:
        app_label = 'djpcms'
    
    
class Page(TimeStamp, PageInterface):
    '''The page model holds several information regarding pages in the sitemap.'''
    template_model = InnerTemplate
    
    title = field.CharField()
    link = field.CharField()
    url = field.SymbolField()
    inner_template = field.ForeignKey(InnerTemplate, required = False)
    template = field.CharField()
    in_navigation = field.IntegerField(default=1)
    body_class = field.CharField(required = False)
    # Access
    requires_login = field.BooleanField(default = False)
    soft_root = field.BooleanField(default=False)
    doctype = field.IntegerField(default = html.htmldefaultdoc)
    insitemap = field.BooleanField(default = True)
    layout = field.IntegerField(default = 0, required = False)

    class Meta:
        app_label = 'djpcms'

    def __unicode__(self):
        return self.url
    
    def blocks(self):
        return self.blockcontents.all()

    def published(self):
        return self in Page.objects.published()
    published.boolean = True
    
    @property
    def additional_head(self):
        return self.additionaldata.filter(where = 1)
    
    def numblocks(self):
        t = self.inner_template
        return 0 if not t else t.numblocks()
    
    def create_template(self, name, template, blocks):
        t = InnerTemplate(name = name,
                          template = template,
                          blocks = blocks)
        t.save()
        return t
    
    def _get_block(self, block, position = None):
        blocks = BlockContent.objects.filter(page = self, block = block)
        N = blocks.count()
        if position == None:
            b = BlockContent(page = self,block = block,position = N)
            b.save()
            return b
        else:
            return blocks.get(position = position)
            
    
class BlockManager(orm.Manager,BlockContentManager):
    pass


class BlockContent(BlockInterface, ModelBase):
    '''A block content object is responsible storing :class:`djpcms.plugins.DJPplugin`
and for maintaining their position in a :class:`djpcms.models.Page`.
    '''
    page           = field.ForeignKey(Page, related_name = 'blockcontents')
    block          = field.IntegerField()
    position       = field.IntegerField(default = 0, index = False)
    arguments      = field.CharField()
    plugin_name    = field.SymbolField(required = False, index = False)
    container_type = field.SymbolField(required = False, index = False)
    title          = field.CharField(required = False)
    for_not_authenticated = field.BooleanField(default = False, index = False)
    requires_login = field.BooleanField(default = False, index = False)
    layout = field.CharField()
    children = field.ListField('BlockContent')
    
    objects = BlockManager()
    
    class Meta:
        app_label = 'djpcms'
        

class SiteContent(TimeStamp,MarkupMixin):
    '''Store content for your web site. It can store markup or raw HTML.'''
    title = field.CharField()
    body = field.CharField()
    markup = field.CharField()
    tags = field.CharField()
    '''Markup type. If not specified it will be treated as raw HTML.'''
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        app_label = 'djpcms'


class AdditionalPageData(ModelBase):
    page    = field.ForeignKey(Page, related_name = 'additionaldata')
    where   = field.IntegerField(default = 1)
    body    = field.CharField()
    
    def __unicode__(self):
        return self.body
    
    class Meta:
        app_label = 'djpcms'

    
class TreeUpdate(object):
    
    def __init__(self):
        self.sites = []
        
    def register_site(self, site):
        '''Provided for testing purposes'''
        if site not in self.sites:
            self.sites.append(site)
        
    def unregister_site(self, site):
        '''Provided for testing purposes'''
        if site in self.sites:
            self.sites.remove(site)
    
    def __call__(self, sender, instance = None, **kwargs):
        '''Register the page post save with tree'''
        if isinstance(instance, Page):
            for site in self.sites:
                if site.tree:
                    site.tree.update_flat_pages()

tree_update = TreeUpdate()

orm.post_save.connect(tree_update, sender = Page)
