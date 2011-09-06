import os
import time

from sphinx import application as Sphinx

import djpcms
from djpcms.utils import gen_unique_id
from djpcms.utils.markups import application

from py2py3 import StringIO

from .builders import SingleStringHTMLBuilder

def info(self, *args,**kwargs):
    pass



class DjpSphinx(Sphinx.Sphinx):
    '''Need to hack sphinx since there is no proper way to manage configuration
without a config file. The problem are the extensions.'''
    def __init__(self, srcdir, outdir, doctreedir, buildername,
                 confoverrides, freshenv=False, tags=None):
        extensions = confoverrides.get('extensions',{})
        confoverrides = confoverrides or {}
        self.next_listener_id = 0
        self._extensions = {}
        self._listeners = {}
        self.domains = Sphinx.BUILTIN_DOMAINS.copy()
        self.builderclasses = Sphinx.BUILTIN_BUILDERS.copy()
        self.builder = None
        self.env = None

        self.srcdir = srcdir
        self.confdir = None
        self.outdir = outdir
        self.doctreedir = doctreedir
        self._status = StringIO()
        self._warning = StringIO()
        self.quiet = True
        self._warncount = 0
        self.warningiserror = False

        self._events = Sphinx.events.copy()

        # status code for command-line application
        self.statuscode = 0

        # read config
        self.tags = Sphinx.Tags(tags)
        self.config = Sphinx.Config(None, None, confoverrides, self.tags)
        self.config.check_unicode(self.warn)
        self.confdir = self.srcdir
        for e in extensions:
            if e not in self.config.extensions:
                self.config.extensions.append(e)

        # backwards compatibility: activate old C markup
        self.setup_extension('sphinx.ext.oldcmarkup')
        # load all user-given extension modules
        for extension in self.config.extensions:
            self.setup_extension(extension)
        # the config file itself can be an extension
        if self.config.setup:
            self.config.setup(self)

        # now that we know all config values, collect them from conf.py
        self.config.init_values()
        # set up translation infrastructure
        self._init_i18n()
        # set up the build environment
        self._init_env(freshenv)
        # set up the builder
        self._init_builder(buildername)
        
    def info(self, *args,**kwargs):
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
                       self.outdir,
                       self.srcdir,
                       SingleStringHTMLBuilder.name,
                       confoverrides=self.confoverrides)
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
