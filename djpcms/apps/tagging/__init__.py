from djpcms import forms, views, UnicodeMixin
from djpcms.apps import archive

__all__ = ['cleaned_tags',
           'TagView',
           'TagMixedIn',
           'TagArchiveView',
           'TagApplication',
           'ArchiveTaggedApplication']

DEFAULT_SEP = ' '


def cleaned_tags(data, separator = DEFAULT_SEP):
    '''Generator of well formatted tags. It splits the string ``data``
using the ``separator`` and removes trailing spaces.'''
    if not data:
        raise StopIteration
    data = data.strip().split(separator)
    for value in data:
        value = value.strip()
        if value:
            yield value
 
 
class TagSet(UnicodeMixin):
     
    def __init__(self, tags):
        self.tags = tags

    def add(self, tag):
        self.tags.add(tag)

    def __unicode__(self):
        return ' '.join(self.tags)
    

class TagField(forms.ChoiceField):
    '''A specialized field for tags'''
    autocomplete = True
    multiple = True

    def taggen(self, value, bfield):
        supclean = super(TagField,self)._clean    
        for tag in cleaned_tags(value,self.separator):
            try:
                tag = supclean(tag,bfield)
            except forms.ValidationError:
                continue
            else:
                if tag:
                    yield tag
    
    def clean(self, value, bfield):
        return TagSet(set(self.taggen(value,bfield)))
        
        
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


class TagView(views.SearchView):
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


class TagMixedIn(object):
    
    def tag(self, djp, n = 1):
        return djp.getdata('tag{0}'.format(n))


class TagApplication(views.Application,TagMixedIn):
    search   = views.SearchView()
    tag0     = views.SearchView('tags/', has_plugins = False)
    tag1     = TagView('<tag1>/', parent_view = 'tag0', has_plugins = False)
    
    def tagurl(self, request, *tags):
        return tagurl(self, request, *tags)
        
    def object_content(self, djp, obj):
        c = super(TagApplication,self).object_content(djp, obj)
        return add_tags(self, c, djp, obj)


class ArchiveTaggedApplication(archive.ArchiveApplication,TagMixedIn):
    '''
    Comprehensive Tagged Archive Application urls.
    '''
    search = archive.ArchiveView()
    year_archive = archive.YearArchiveView('<year>/', has_plugins = False)
    month_archive = archive.MonthArchiveView('<month>/',
                                             parent_view = 'year_archive',
                                             has_plugins = False)
    day_archive = archive.DayArchiveView('<day>/',
                                         parent_view = 'month_archive',
                                         has_plugins = False)
    
    tag0 = views.ModelView('tags/', has_plugins = False)
    tag1 = TagArchiveView('<tag1>/', parent_view = 'tag0', has_plugins = False)
    year_archive1 = TagArchiveView('<year>/',  parent_view = 'tag1')
    month_archive1 = TagArchiveView('<month>/', parent_view = 'year_archive1')
    day_archive1 = TagArchiveView('<day>/',   parent_view = 'month_archive1')
     
    def tagurl(self, request, *tags):
        return tagurl(self, request, *tags)
    
    def object_content(self, djp, obj):
        c = super(ArchiveTaggedApplication,self).object_content(djp, obj)
        return c
        return add_tags(self, c, djp, obj)
    


