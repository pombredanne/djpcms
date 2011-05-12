'''\
Djpcms models can be django based or stdnet based.
'''
from djpcms import sites, dispatch

if sites.settings.CMS_ORM == 'django':
    
    from djpcms.core.cmsmodels._django import *
    from django.db.models.signals import post_save
    
elif sites.settings.CMS_ORM == 'stdnet':
    
    from djpcms.core.cmsmodels._stdnet import *
    from stdnet.orm import post_save
    
else:
    BlockContent = None
    Page = None
    Site = None
    InnerTemplate = None
    SiteContent = None
    tree_update = None
    
    

if Page:
    
    class TreeUpdate(object):
        
        def __init__(self):
            self.sites = []
            self.sites.append(sites)
            
        def register_site(self, site):
            '''Provided for testing purposes'''
            if site not in self.sites:
                self.sites.append(site)
            
        def unregister_site(self, site):
            '''Provided for testing purposes'''
            if site in self.sites:
                self.sites.remove(site)
        
        def update_sitemap_tree(self, sender, instance = None, **kwargs):
            '''Register the page post save with tree'''
            if isinstance(instance, Page):
                for site in self.sites:
                    if site.tree:
                        site.tree.update_flat_pages()
    
    tree_update = TreeUpdate()
    
    post_save.connect(tree_update.update_sitemap_tree, sender = Page)

