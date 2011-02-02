import sys
import ctypes

from .base import Platform as PlatformBase


class Platform(PlatformBase):
    
    def isPosix(self):
        return True