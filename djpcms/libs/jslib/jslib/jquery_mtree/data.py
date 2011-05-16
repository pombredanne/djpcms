'''djpcms classes for serializing objects to be used in mtree
plugin'''
from djpcms.utils.ajax import HeaderBody

PLUGIN = 'mtree'


class MtreeException(Exception):
    pass


class JSONMtree(HeaderBody):
    _header = '{0}-data'.format(PLUGIN)

    def header(self):
        return self._header


class JSONError(JSONMtree):
    _header = '{0}-error'.format(PLUGIN)
    
    def __init__(self, msg):
        self.msg = msg
    
    def body(self):
        return self.msg
    

class JSONdata(JSONMtree):
    
    def __init__(self, fields = None, views = None, action = 'reload'):
        self.children = []
        self._body = {'action':action,
                      'children': self.children,
                      'views':views,
                      'fields':fields}
    
    def add(self, js):
        self.children.append(js.body())
            
    def body(self):
        return self._body    


class JSONPortfolio(JSONMtree):
    _header = '{0}-node'.format(PLUGIN)
    
    def __init__(self, id, name,
                 folder = False,
                 movable = False,
                 type = 'default',
                 children = None,
                 values = None,
                 action = 'reload'):
        self._body = {'name': name,
                      'id': id,
                      'type': type,
                      'folder': folder,
                      'movable': movable,
                      'values': values,
                      'children': children}
    
    def body(self):
        return self._body
    