import datetime
import json

from djpcms import views
from djpcms.template import loader, mark_safe
from djpcms.utils.unipath import FSPath as Path

    
class DocView(views.View):
    '''Sphinx documentation view.'''
    editurl          = None
    
    def __init__(self, regex = '(?P<url>[\w./-]*)', lang = False,
                 version = False, in_navigation = True, **kwargs):
        super(DocView,self).__init__(regex = regex, in_navigation = in_navigation, **kwargs)
        self.lang    = lang
        self.version = version
    
    def old_get_url(self, djp, **urlargs):
        lang = urlargs.get('lang','')
        vers = urlargs.get('version','')
        urls = urlargs.get('url','')
        url  = self.appmodel.baseurl
        if lang:
            url = '%s/%s/' % (url,lang)
        if vers:
            url = '%s/%s/' % (url,vers)
        if urls:
            url = '%s/%s/' % (url,urls.strip('/'))
        return url

    def render(self, djp):
        app     = self.appmodel
        request = djp.request
        args    = djp.kwargs
        page    = djp.page
        lang    = args.get('lang',app.deflang)
        version = args.get('version',app.defversion)
        url     = args.get('url','')
        docroot = self.appmodel.get_docroot(djp, lang, version)
    
        # First look for <bits>/index.fpickle, then for <bits>.fpickle
        bits = url.strip('/').split('/') + ['%s.fjson' % app.master_doc]
        doc = docroot.child(*bits)
        if not doc.exists():
            bits = bits[:-2] + ['%s.fjson' % bits[-2]]
            doc = docroot.child(*bits)
            if not doc.exists():
                raise djp.http.Http404("'%s' does not exist" % doc)

        bits[-1] = bits[-1].replace('.fjson', '')
        name  = self.appmodel.name
        namet = '-'.join([b for b in bits if b])
        namet = app.name_template_mapping.get(namet,namet)
        template_names = [
                          'docs/%s.html' % namet,
                          'djpcms/docs/%s.html' % namet,
                          'docs/doc.html',
                          ]
        doc = json.load(open(doc, 'rb'))
        rels = []
        for link in doc.get('rellinks',[]):
            rels.append({'url': '%s%s/' % (app.baseurl,link[0]),
                         'title': link[1]})
        doc['rellinks'] = rels
        djp.breadcrumbs = self.makebreadcrumbs(djp,doc)
        c = {'doc':     doc,
             'env':     json.load(open(docroot.child('globalcontext.json'), 'rb')),
             'lang':    lang,
             'version': version,
             'docurl':  url,
             'update_date': datetime.datetime.fromtimestamp(docroot.child('last_build').mtime()),
             #'home': urlresolvers.reverse('document-index', kwargs={'lang':lang, 'version':version}),
             #'search': urlresolvers.reverse('document-search', kwargs={'lang':lang, 'version':version}),
             'redirect_from': request.GET.get('from', None)}
        
        return loader.render_to_string(template_names, c)
        
    def makebreadcrumbs(self, djp, doc):
        parent = djp
        if djp.kwargs:
            parent = parent.parent
        parents = doc.get('parents',[])
        b = []
        while parent:
            b.append({'name': parent.title,
                      'url':  parent.url})
            parent = parent.parent
        b = list(reversed(b))
        for parent in parents:
            b.append({'url': parent.get('link',''),
                      'name': parent.get('title','')})
        if djp.kwargs:
            title = doc.get('title','')
            if not title:
                title = doc.get('indextitle','')
            b.append({'name': title})
        for p in range(djp.settings.ENABLE_BREADCRUMBS):
            b.pop(0)
        if b:
            b[-1].pop('url',None)
        return b


class DocApplication(views.Application):
    deflang          = 'en'
    '''Default language. Default ``en``.'''
    defversion       = 'dev'
    '''Default version. Default ``dev``.'''
    DOCS_PICKLE_ROOT = None
    '''Root class for serialized documentation. Default ``None``.'''
    master_doc       = 'index'
    '''Specify sphinx master doc. Default ``index``.'''
    name_template_mapping = {'py-modindex':'modindex'}
    '''Dictionary which maps names to template names.'''
    
    index = DocView(regex = '')
    document = DocView(parent = 'index')
    
    def __init__(self, baseurl, editavailable = False, **kwargs):
        super(DocApplication,self).__init__(baseurl, editavailable=editavailable, **kwargs)
    
    def get_path_args(self, lang, version):
        return (lang, version, "_build", "json")
    
    def get_docroot(self, djp, lang, version):
        docroot = Path(self.DOCS_PICKLE_ROOT).child(*self.get_path_args(lang, version))
        if not docroot.exists():
            raise djp.http.Http404()
        return docroot 
    
    def bodybits(self):
        if self.editurl:
            return mark_safe('class="edit documentation"')
        else:
            return mark_safe('class="documentation"')
        
    def doc_index_url(self, request, lang, version):
        return '%s%s/%s/' % (self.baseurl,lang,version)
    
    def table_of_content_url(self, request, lang, version):
        return '%s%s/' % (self.doc_index(),'contents')
    
    class Media:
        js = ['djpcms/sphinx/deco.js']
        css = {
            'all': ('djpcms/sphinx/smooth.css',)
        }
