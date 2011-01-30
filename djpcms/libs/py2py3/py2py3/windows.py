import os
import time
import sys
import ctypes

from .base import Platform as PlatformBase


class Platform(PlatformBase):
    timer = time.clock
    
    def isWindows(self):
        return True
    
    def isVista(self):
        """
        Check if current platform is Windows Vista or Windows Server 2008.

        @return: C{True} if the current platform has been detected as Vista
        @rtype: C{bool}
        """
        if hasattr(sys, "getwindowsversion"):
            return sys.getwindowsversion()[0] == 6
        else:
            return False
        
    def symlink(self,filename,linkname):
        '''Call windows API
        http://msdn.microsoft.com/en-us/library/aa363866'''
        flag = 0x1 if os.path.isdir(filename) else 0x0
        kdll = ctypes.windll.LoadLibrary("kernel32.dll")
        if not kdll.CreateSymbolicLinkA(filename,linkname,flag):
            return self.lasterror()
        
    def lasterror(self):
        kdll = ctypes.windll.LoadLibrary("kernel32.dll")
        return kdll.GetLastError()

        
    