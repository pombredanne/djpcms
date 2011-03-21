import os

from djpcms import views
from djpcms.utils.pathtool import uplevel
from djpcms.apps.included import archive, vanilla, docs
from djpcms.models import SiteContent

from .models import Strategy


class ContentArchiveApplication(archive.ArchiveApplication):
    '''
    Simple ArchiveApplication based on the SiteContent model in djpcms
    '''
    inherit    = True
    name       = 'content'
    date_code  = 'last_modified'


class DocTestApplication(docs.DocApplication):
    inherit    = True
    deflang    = None
    defversion = None
    name       = 'test_documentation'
    DOCS_PICKLE_ROOT = uplevel(os.path.abspath(__file__))
    
    def get_path_args(self, lang, version):
        return ('docs',)
    
    
#Register few applications for testing
appurls = (
           archive.ArchiveApplication('/content/',
                                      SiteContent, 
                                      name = 'content',
                                      date_code  = 'last_modified'),
           DocTestApplication('/docs/'),
           vanilla.Application('/strategies/', Strategy),
           )