from djpcms import sites, dispatch
from djpcms.forms import post_save

if sites.settings.CMS_ORM == 'django':
    
    from djpcms.core.cmsmodels._django import *
    
elif sites.settings.CMS_ORM == 'stdnet':
    
    from djpcms.core.cmsmodels._stdnet import *
    
else:
    BlockContent = None
    Page = None
    Site = None
    InnerTemplate = None
    SiteContent = None
    

if Page:
    
    def update_sitemap_tree(sender, instance = None, **kwargs):
        if isinstance(instance, Page):
            root = sender.root
            if root:
                root.tree.drop_flat_pages()
            
    post_save.connect(update_sitemap_tree)
    