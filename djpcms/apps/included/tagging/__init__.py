from djpcms import forms
from djpcms.views import appsite, appview
from djpcms.apps.included.archive import ArchiveApplication, views as archive

#from tagging.models import Tag, TaggedItem


# REGEX FOR A TAG
tag_regex = '[-\.\+\#\'\:\w]+'


def add_tags(self, c, djp, obj):
    request = djp.request
    tagurls = []
    tagview = self.getview('tag1')
    if obj.tags and tagview:
        tags = obj.tags.split()
        for tag in tags:
            djp = tagview(request, tag1 = tag)
            tagurls.append({'url':djp.url,
                            'name':tag})
    c['tagurls'] = tagurls
    return c


def tagurl(self, request, *tags):
    view = self.getview('tag%s' % len(tags))
    if view:
        kwargs = {}
        c = 1
        for tag in tags:
            kwargs['tag%s' % c] = tag
            c += 1
        return view(request, **kwargs).url


class TagView(appview.SearchView):
    '''A specialised search view which handles tags'''
    def __init__(self, *args, **kwargs):
        super(TagView,self).__init__(*args, **kwargs)
    
    def title(self, djp):
        return self.appmodel.tag(djp)
    
    def tags(self, djp):
        tags = []
        for name in self.regex.names:
            tag = djp.getdata(name)
            if tag:
                tags.append(tag)
        return tags
        
    def appquery(self, djp):
        query = super(TagView,self).appquery(djp)
        tags = self.tags(djp)
        if tags:
            return TaggedItem.objects.get_by_model(query, tags)
        else:
            return query


class TagArchiveView(archive.ArchiveView):
    
    def __init__(self, *args, **kwargs):
        super(TagArchiveView,self).__init__(*args, **kwargs)
    
    def title(self, djp):
        return self.appmodel.tag(djp)
    
    def linkname(self, djp):
        urlargs = djp.kwargs
        return urlargs.get('tag1',None)
        
    def appquery(self, djp):
        query = super(TagArchiveView,self).appquery(djp)
        tags = djp.get('tags',None)
        if tags:
            return TaggedItem.objects.get_by_model(query, tags.values())
        else:
            return query


class TagsApplication(appsite.ModelApplication):
    '''An application for anabling tags autocomplete'''
    search_fields = ['name']
    complete = appview.AutocompleteView()


class TagMixedIn(object):
    
    def tag(self, djp, n = 1):
        return djp.getdata('tag{0}'.format(n))


class TagApplication(appsite.ModelApplication,TagMixedIn):
    search   = appview.SearchView(in_navigation = True)
    tag0     = appview.SearchView(regex = 'tags', parent = 'search', in_navigation = True)
    tag1     = TagView(regex = '(?P<tag1>%s)' % tag_regex, parent = 'tag0')
    
    def tagurl(self, request, *tags):
        return tagurl(self, request, *tags)
        
    def object_content(self, djp, obj):
        c = super(TagApplication,self).object_content(djp, obj)
        return add_tags(self, c, djp, obj)


class ArchiveTaggedApplication(ArchiveApplication,TagMixedIn):
    '''
    Comprehensive Tagged Archive Application urls.
    '''
    search        = archive.ArchiveView()
    year_archive  = archive.YearArchiveView(regex = '(?P<year>\d{4})')
    month_archive = archive.MonthArchiveView(regex = '(?P<month>\w{3})', parent = 'year_archive')
    day_archive   = archive.DayArchiveView(regex = '(?P<day>\d{2})',   parent = 'month_archive')
    
    tag0           = appview.ModelView(regex = 'tags', in_navigation = True)
    tag1           = TagArchiveView(regex = '(?P<tag1>%s)' % tag_regex, parent = 'tag0')
    year_archive1  = TagArchiveView(regex = '(?P<year>\d{4})',  parent = 'tag1')
    month_archive1 = TagArchiveView(regex = '(?P<month>\w{3})', parent = 'year_archive1')
    day_archive1   = TagArchiveView(regex = '(?P<day>\d{2})',   parent = 'month_archive1')
     
    def tagurl(self, request, *tags):
        return tagurl(self, request, *tags)
    
    def object_content(self, djp, obj):
        c = super(ArchiveTaggedApplication,self).object_content(djp, obj)
        return add_tags(self, c, djp, obj)
    
    
class TagField(forms.CharField):
    
    def _handle_params(self, choices = None, separator = ' ', **kwargs):
        self.choices = choices
        self.separator = separator
        self._raise_error(kwargs)

