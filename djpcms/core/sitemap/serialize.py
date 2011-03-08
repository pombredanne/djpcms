from djpcms.utils.ajax import HeaderBody

__all__ = ['JsonTreeError',
           'JsonData',
           'JsonTreeNode',
           'JsonTreeException',
           'tree_error']

class JsonTreeException(Exception):
    pass


class JsonTreeError(HeaderBody):
    
    def __init__(self, msg):
        self.msg = msg
        
    def header(self):
        return 'tree-error'
    
    def body(self):
        return self.msg
    
    
class JsonTree(HeaderBody):
    children = None
    
    def add(self, js):
        if self.children is not None:
            self.children.append(js.body())
    
    def body(self):
        return self._body
        
        
class JsonData(JsonTree):
    
    def __init__(self, fields = None, views = None, action = 'reload'):
        self.children = []
        self._body = {'action':action,
                      'children': self.children,
                      'views':views,
                      'fields':fields}
        
    def header(self):
        return 'tree-data'
    

class JsonTreeNode(JsonTree):
    
    def __init__(self, id, name,
                 folder = False,
                 movable = False,
                 type = 'default',
                 children = None,
                 values = None,
                 action = 'reload'):
        self.children = children if children is not None else self.children
        self._body = {'name': name,
                      'id': id,
                      'type': type,
                      'folder': folder,
                      'movable': movable,
                      'values': values,
                      'children': self.children}
    
    def header(self):
        return 'tree-node'
    
    
def tree_error(f):
    '''Decorator to be applied to a member function
    returning an instance of :class:`JsonTree`.
    It will catch :class:`JsonTreeException`.'''
    def _(*args,**kwargs):
        try:
            return f(*args,**kwargs)
        except PortfolioError as e:
            return JSONError(to_string(e))
    return _
