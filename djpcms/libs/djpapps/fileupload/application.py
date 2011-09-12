try:
    import Image
except ImportError:
    Image = None
    
from djpcms import views, ispy3k
from djpcms.apps.included.vanilla import Application
from djpcms.utils import mark_safe
from djpcms.core import files

if ispy3k:
    from io import BytesIO
else:
    from StringIO import StringIO as BytesIO

from .forms import FileUploadForm


class FileApplication(Application):
    inherit = True
    storage = None
    tumbnail_height = 128
    tumbnail_width = 128
    form = FileUploadForm
    
    add = views.AddView()
    
    def __init__(self, *args, **kwargs):
        self.storage = kwargs.pop('storage',self.storage)
        super(FileApplication,self).__init__(*args, **kwargs)
    
    def registration_done(self):
        storage = self.storage
        if hasattr(storage,'__call__'):
            storage = storage()
        if storage:
            self.site.storage = storage
        self.model.register_signals()
    
    def save_file(self, name, file):
        return self.model(name = name,
                          size = file.size,
                          content_type = file.content_type).save()
        
    def objectfunction__thumbnail(self, instance):
        storage = self.site.storage
        if storage:
            ct = instance.content_type
            cts = ct.split('/')
            if cts[0] == 'image':
                name = instance.name
                tname = 'T_{0}x{1}_{2}'.format(self.tumbnail_width,
                                               self.tumbnail_height,name)
                if not storage.exists(tname) and Image:
                    f = storage.open(name)
                    im = Image.open(f.file)
                    im.thumbnail((self.tumbnail_width, self.tumbnail_height),
                                  Image.ANTIALIAS)
                    buff = BytesIO()
                    fn = im.save(buff, format = cts[1])
                    storage.save(files.File(buff,tname,instance.content_type))
                
                if storage.exists(tname):    
                    turl = storage.url(tname)
                    #url = storage.url(instance.name)
                    return '<img src="{0}"/>'.format(turl)
                    #return mark_safe('<a href="{0}"><img src="{1}"/></a>'\
                    #                 .format(url,turl))
            