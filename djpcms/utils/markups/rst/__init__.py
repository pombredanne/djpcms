import os
import time
from docutils.core import publish_parts

from sphinx import application as Sphinx
import djpcms
from djpcms.utils import gen_unique_id
from djpcms.utils.markups import application

from .builders import SingleStringHTMLBuilder

def info(self, *args,**kwargs):
    pass


Sphinx.info = info


class DjpSphinx(Sphinx.Sphinx):
    pass


class Application(application.Application):
    code = 'rst'
    name = 'reStructuredText'
    _setup = None
    
    def setup(self):
        settings = djpcms.sites.settings
        cfgdir = settings.SITE_DIRECTORY
        smod = settings.SITE_MODULE
        outdir = os.path.join(cfgdir,'media',smod,self.code)
        srcdir = os.path.join(outdir,'_tmp')
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        if not os.path.exists(srcdir):
            os.mkdir(srcdir)
        self.srcdir = srcdir
        self.confoverrides = settings.SPHINX
        self.outdir = outdir
        self.media_url = '{0}{1}/{2}/'.format(settings.MEDIA_URL,smod,self.code)
        
    def __call__(self, text):
        if not self._setup:
            self.setup()
            self._setup = True
        sx = DjpSphinx(self.srcdir,
                       None,
                       self.outdir,
                       self.srcdir,
                       SingleStringHTMLBuilder.name,
                       confoverrides=self.confoverrides,
                       status = None,
                       warning = None)
        sx.media_url = self.media_url
        master_doc = gen_unique_id()
        mc = (master_doc,'env')
        sx.config.values['master_doc'] = mc
        sx.config.config_values['master_doc'] = mc
        fname = os.path.join(self.srcdir,'{0}.rst'.format(master_doc))
        fdoc = os.path.join(self.srcdir,'{0}.doctree'.format(master_doc))
        f = open(fname,'w')
        f.write(text)
        f.close()
        sx.build(force_all=True)
        res = sx.builder.docwriter.parts['fragment']
        os.remove(fname)
        os.remove(fdoc)
        return res
    
    
app = Application()
