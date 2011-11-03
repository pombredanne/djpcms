import os

from djpcms.utils import locks
from djpcms.utils.urls import urlbits, urlfrombits

from .base import Filehandler, File

__all__ = ['Disk','Disksite']

class Disk(Filehandler):
    
    def __init__(self, location=None, base_url=None, permission = None):
        self.location = os.path.abspath(location)
        self.base_url = base_url
        self.permission = permission
        
    def path(self, name):
        return os.path.join(self.location,name)
    
    def exists(self, name):
        return os.path.exists(self.path(name))
        
    def open(self, name, mode='rb'):
        return File(open(self.path(name), mode))
    
    def delete(self, name):
        name = self.path(name)
        if os.path.exists(name):
            os.remove(name)
    
    def url(self, name):
        return os.path.join(self.base_url,name)
    
    def _save(self, name, content):
        full_path = self.path(name)

        directory = os.path.dirname(full_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif not os.path.isdir(directory):
            raise IOError("%s exists and is not a directory." % directory)

        # There's a potential race condition between get_available_name and
        # saving the file; it's possible that two threads might return the
        # same name, at which point all sorts of fun happens. So we need to
        # try to create the file, but if it already exists we have to go back
        # to get_available_name() and try again.

        while True:
            try:
                # This file has a file path that we can move.
                if hasattr(content, 'temporary_file_path'):
                    file_move_safe(content.temporary_file_path(), full_path)
                    content.close()

                # This is a normal uploadedfile that we can stream.
                else:
                    # This fun binary flag incantation makes os.open throw an
                    # OSError if the file already exists before we open it.
                    fd = os.open(full_path, os.O_WRONLY | os.O_CREAT |\
                                  os.O_EXCL | getattr(os, 'O_BINARY', 0))
                    try:
                        locks.lock(fd, locks.LOCK_EX)
                        for chunk in content.chunks():
                            os.write(fd, chunk)
                    finally:
                        locks.unlock(fd)
                        os.close(fd)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    # Ooops, the file exists. We need a new file name.
                    name = self.get_available_name(name)
                    full_path = self.path(name)
                else:
                    raise
            else:
                # OK, the file save worked. Break out of the loop.
                break

        if self.permission is not None:
            os.chmod(full_path, self.permission)

        return name
    

class Disksite(object):
    
    def __init__(self, location=None):
        self.location = location
        
    def __call__(self, settings):
        base = settings.SITE_DIRECTORY
        name = settings.SITE_MODULE
        media = settings.MEDIA_URL
        location = self.location or 'filefolder'
        bits = urlbits(location)
        location = os.path.join(base,'media',name,*bits)
        base_url = '{0}{1}{2}'.format(media,name,urlfrombits(bits))
        return Disk(location,base_url)
        