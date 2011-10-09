from djpcms.utils import urlencode

__all__ = ['Paginator']


sorting_values = {'asc':'','desc':'-'}

class Paginator(object):
    '''
    List pagination
    It contains Information about the items displayed and a list of links to
    navigate through the search.
    '''
    
    def __init__(self, total = 0, per_page = 20,
                 numends = 2, maxentries = 15, 
                 page_menu = None, page = 1,
                 start = 0):
        '''
        @param data:       queryset
        @param page:       page to display
        @param per_page:   number of elements per page
        @param maxentries: Max number of links in the pagination list
        '''
        self.total = total
        self.per_page = max(int(per_page),1)
        self.hentries = max(int(maxentries)/2,2)
        self.numends = numends
        tp = int(self.total/self.per_page)
        if self.per_page*tp < self.total:
            tp += 1
        self.pages = tp
        self.multiple = self.pages > 1
        start = int(start)
        page = int(start/self.per_page)
        if page*self.per_page <= start:
            page += 1
        self.page = page
        end = self.page*self.per_page
        self.start = end - self.per_page
        self.end = min(end,self.total)
        if self.multiple:
            self.page_menu = page_menu
        else:
            self.page_menu = None
            
    def slice_data(self, data):
        return data[self.start:self.end]
        
    def render(self):
        return self.navigation()
        
    def pagenumber(self, request, data):
        '''
        Get page information form request
        The page should be stored in the request dictionary
        '''
        d = dict(request.REQUEST.items())
        page = 1
        if 'page' in d:
            try:
                page = int(d.pop('page'))
            except:
                pass
        sort_by = {}
        for k,v in d.items():
            s = sorting_values.get(v,None)
            if s is not None:
                try:
                    data = data.sort_by('{0}{1}'.format(s,k))
                except:
                    pass
        self.qs = data
        self.datadict = urlencode(d)
        return max(min(page,self.pages),1)
    
    def navigation(self):
        if self.pages == 1:
            return ''
        return ''
        ul   = linklist()
        
        # Left links
        if self.page > 1:
            # page is over half-entries. Insert the left link
            if self.page > self.hentries:
                _pagination_entry(ul, prevend, retdata, '', step, total, cn = 'pagination-left-link')
        
        # Right links
        if self.pages < self.pages:
            p = self.page + 1
            while p <= self.pages:
                self._pagination_entry(ul, p)
                p += 1
        return ul            
    
    def _pagination_entry(self, ul, p, cn = None):
        data['_page'] = p
        en  = p*self.per_page
        st  = en - self.per_page + 1
        en  = min(en,self.total) 
        url = datatourl(url, data)
        title = 'page %s from %s to %s' % (p,st,en)
        ul.addlistitem(c, self.url, title = title, cn = cn)
        