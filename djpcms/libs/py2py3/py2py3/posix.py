import sys
import ctypes

from .base import PlatForm as PlatFormBase


class PlatForm(PlatFormBase):
    
    def isPosix(self):
        return True