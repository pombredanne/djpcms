from djpcms import to_string
from djpcms.html import HtmlWidget
from djpcms.utils import gen_unique_id
from djpcms.utils.text import nicename
from djpcms.utils.ajax import jempty

from .data import JSONdata, JSONError, JSONPortfolio, MtreeException


class jok(jempty):
    
    def header(self):
        return 'ok'


def mtree_error(f):
    '''Decorator for mtree ajax functions.'''
    def _(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except MtreeException as e:
            return JSONError(to_string(e))
    return _


class MtreeView(object):
    '''View for displaying the tree'''
    
    def get_child_from_id(self, djp):
        '''Return a child node from an ide in the request object'''
        raise NotImplementedError
    
    def get_root_tree(self, djp):
        '''Fetch the root object for the tree. Must be
implemented by derived classes. The root object must have the
``tojson`` method.'''
        raise NotImplementedError
    
    @mtree_error
    def ajax__reload(self, djp):
        appmodel = self.appmodel
        root = self.get_root_tree(djp)
        fields = appmodel.fields
        if hasattr(fields,'__call__'):
            fields = fields(djp)
        else:
            fields = [{'name':name,'description':nicename(name)} for name in fields]
        return root.tojson(fields = fields,
                           views = appmodel.table_views,
                           refresh = True)
    
    @mtree_error
    def ajax__rename(self, djp):
        elem = self.get_child_from_id(djp)
        params = dict(djp.request.POST.items())
        name = params.get('name',None)
        if not name:
            raise MtreeException('No name available')
        elem.name = name
        elem.save()
        return jok()
    
    @mtree_error
    def ajax__delete(self, djp):
        elem = self.get_child_from_id(djp)
        if elem:
            elem.delete()
        return jok()


class MtreeMixin(object):
    '''A mixin to be used in :class:`djpcms.views.Application`.
It implements several mtree specific functions.'''

    MTREE_JAVASCRIPT = (
                        'djpkit/djpkit.js',
                        'djpkit/jquery.splitter.js',
                        'jquery_mtree/mtree.js',
                        'jquery_mtree/mtree.crrm.js',
                        'jquery_mtree/mtree.ui.js',
                        'jquery_mtree/mtree.table.js',
                        'jquery_mtree/mtree.dnd.js',
                        'jquery_mtree/mtree.contextmenu.js',
                        'jquery_mtree/mtree.types.js',
                        'jquery_mtree/mtree.djpcms.js'
                        )
    
    '''View to display Sitemap on a table-tree'''
    fields = ('id',)
    table_views = [
             {'name':'default',
              'fields': ('id',)},
             ]
    
    _mtree = {
             'plugins': ('core','json','crrm','ui','table','types')
             }
    
    def mtree(self, djp):
        '''Return dictionary of mtree options'''
        for k,v in self._mtree.items():
            yield k,v
    
    def get_widgetid(self, djp):
        '''This function should return a unique ID for the tree.
Its value will be used as HTML id for the tree widget.'''
        return gen_unique_id()
        
    def widget(self, djp):
        '''Create the widget element with metadata which will be passed to the
javascript plugin as options.'''
        id = self.get_widgetid(djp)
        return HtmlWidget('div', id = id, cn = 'mtree')

    def render_tree(self, djp):
        '''reder the widget for a mtree'''
        url = djp.url
        pdiv = self.widget(djp)
        for k,v in self.mtree(djp):
            pdiv.addData(k,v)
        pdiv.addData('json',{'url': djp.url})
        return pdiv.render()
    
    
class TableItem(object):
    '''A mixin class for portfolio items. Both portfolios and 
position implementation should derive from this class.'''
    
    def get_type(self):
        raise NotImplementedError
    
    def movable(self):
        return True
    
    def copyable(self):
        return True
    
    def groupname(self):
        raise NotImplementedError
    
    def mapper(self):
        if not hasattr('_mapper',self):
            self._mapper = mapper(self)
        return self._mapper
    
    def get_parent(self):
        raise NotImplementedError
    
    def is_child(self, parent):
        '''\
Check if self is a child of ``parent``.

:parameter parent: the parent element to check.'''
        raise NotImplementedError
    
    def absolute_id(self):
        '''Absolute ID for the Portfolio Item'''
        return self.relativeurl()
        #return self.mapper.absolute_id(self)
    
    def relativeurl(self):
        if self.isportfolio():
            return 'p-{0}'.format(self.id)
        else:
            return 't-{0}'.format(self.id)
        
    def todict(self):
        if self.isportfolio():
            yield {'isportfolio': self.isportfolio(),
                   'movable': self.movable()}
            
    def get_tree(self):
        for portfolio in instance.executed.all():
            yield portfolio.to_table_row()
        for trade in instance.executed.all():
            yield trade.to_table_row()
            
    def tojson(self, djp, action = None):
        folder = self.isportfolio()
        if folder:
            children = [child.tojson(djp).body() for child in self.get_children()]
        else:
            children = None
        appmodel = djp.view.appmodel
        values = dict((name,appmodel.field(name,self)) for name in appmodel.fields)
        js = JSONPortfolio(id = self.absolute_id(),
                           name = self.name,
                           type = self.get_type(),
                           folder = folder,
                           values = values,
                           children = children)
        if action == 'reload':
            djs = JSONdata(fields = appmodel.fields,
                           views = appmodel.field_views(djp),
                           action = action)
            djs.add(js)
            return djs
        else:
            return js
    
    def get_children(self):
        raise NotImplementedError
             
