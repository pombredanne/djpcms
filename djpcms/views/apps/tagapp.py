'''
Requires django-tagging

Battery included plugins and application for tagging and tagging with archive
'''
from djpcms.views import appsite
from djpcms.views.appview import AppView, ArchiveView

       
class TagArchiveView(ArchiveView):
    
    def __init__(self, *args, **kwargs):
        super(TagArchiveView,self).__init__(*args, **kwargs)
        
    def appquery(self, request, year = None, month = None, day = None, **tags):
        query = super(TagArchiveView,self).appquery(request, year = year, month = month, day = day)
        if tags:
            return TaggedItem.objects.get_by_model(query, tags.values())
        else:
            return query


class ArchiveTaggedApplication(appsite.ArchiveApplication):
    '''
    Comprehensive Tagged Archive Application urls
    '''
    search         =    ArchiveView(in_navigation = True)
    year_archive   =    ArchiveView(regex = '(?P<year>\d{4})',
                                    parent = 'search')
    month_archive  =    ArchiveView(regex = '(?P<month>\w{3})',
                                    parent = 'year_archive')
    day_archive    =    ArchiveView(regex = '(?P<day>\d{2})',
                                    parent = 'month_archive')
    tag1           = TagArchiveView(regex = 'tags/(?P<tag1>\w+)',
                                    parent = 'search')
    year_archive1  = TagArchiveView(regex = '(?P<year>\d{4})',
                                    parent = 'tag1')
    month_archive1 = TagArchiveView(regex = '(?P<month>\w{3})',
                                    parent = 'year_archive')
    day_archive1   = TagArchiveView(regex = '(?P<day>\d{2})',
                                    parent = 'month_archive')
    tag2           = TagArchiveView(regex = 'tags2/(?P<tag1>\w+)/(?P<tag2>\w+)',
                                    parent = 'search')
    year_archive2  = TagArchiveView(regex = '(?P<year>\d{4})',
                                    parent = 'tag2')
    month_archive2 = TagArchiveView(regex = '(?P<month>\w{3})',
                                    parent = 'year_archive2')
    day_archive2   = TagArchiveView(regex = '(?P<day>\d{2})',
                                    parent = 'month_archive2')
    tag3           = TagArchiveView(regex = 'tags3/(?P<tag1>\w+)/(?P<tag2>\w+)/(?P<tag3>\w+)',
                                    parent = 'search')
    year_archive3  = TagArchiveView(regex = '(?P<year>\d{4})',
                                    parent = 'tag3')
    month_archive3 = TagArchiveView(regex = '(?P<month>\w{3})',
                                    parent = 'year_archive3')
    day_archive3   = TagArchiveView(regex = '(?P<day>\d{2})',
                                    parent = 'month_archive3')
    
    def basequery(self, request):
        return self.formodel.objects.all()
    
    def tagurl(self, request, tag):
        view = self.getapp('tag')
        if view:
            return view.requestview(request, tag = tag).get_url()
    
    def object_content(self, request, prefix, wrapper, obj):
        tagurls = []
        tagview = self.getapp('tag')
        if obj.tags and tagview:
            tags = obj.tags.split(u' ')
            for tag in tags:
                tagurls.append({'url':tagview.get_url(request, tag = tag),'name':tag})
        return {'tagurls': tagurls}
    
    
    