import json

from djpcms import sites
from djpcms.models import Page, Site
from djpcms.forms import ValidationError
from djpcms.core.orms import mapper, getid
from djpcms.core.exceptions import ImproperlyConfigured

from .forms import PageForm


def all():
    return mapper(Page).all()


def create_page(parent = None, user = None,
                inner_template = None, commit = True,
                **kwargs):
    '''Create a new page.'''
    if parent:
        data = mapper(Page).model_to_dict(Page)
        data.update(**kwargs)
        if not user:
            user = parent.user
        if not inner_template:
            inner_template = parent.inner_template
        parent = parent.id
        data.update({'parent':parent,
                     'user':getid(user),
                     'inner_template': getid(inner_template),
                     'site':getid(get_current_site())})
    else:
        data = {'site':get_current_site()}
        
    f = PageForm(data = data, parent = parent, model = Page)
    if f.is_valid():
        if commit:
            return f.save(commit = commit)
        else:
            return f
    else:
        raise ValidationError(json.dumps(f.errors))


def get_current_site(request = None):
    '''Retrive the current site object from settings file'''
    if request:
        site_id = request.site.settings.SITE_ID
    else:
        site_id = sites.settings.SITE_ID
    mp = mapper(Site)
    try:
        return mp.get(id = site_id)
    except mp.DoesNotExist:
        all_sites = mp.all()
        if all_sites:
            ids = ', '.join((str(s.id) for s in all_sites))
            raise ImproperlyConfigured('Site ID {0} not available. Available site ids are: {1}'.format(site_id,ids))
        elif site_id == 1:
            site = Site(name = 'example.com', domain = 'example.com')
            site.save()
            return site
        else:
            raise ImproperlyConfigured('No Sites available. Cannot choose site ID {0}'.format(site_id))
    
    
def get_root(request):
    site = get_current_site(request)
    pages = mapper(Page).filter(site = site, parent = None)
    if pages:
        return pages[0]


def get_for_application(djp, code, view_url = None):
    '''Obtain a Page from an application code. If pages are not found check for consistency'''
    site = get_current_site(djp)
    filter = mapper(Page).filter
    pages = filter(site = site, application_view = code)
    if not pages:
        url = view_url or djp.url
        pages = filter(site = site, url = url)
        if pages:
            page = pages[0]
            page.application_view = code
            page.save
            return [page]
    return pages
