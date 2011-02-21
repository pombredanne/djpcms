#
# I use this hack in windows to install libraries from my eclipse
# workspace into the python path.
#
# No need for this in linux since you can use symbolic links
#
import sys
import os

def virtual(*libs):
    '''``libs`` is a tuple of two-dimensional tuples containing,
    the library name and library distribution name.'''
    workspace_dir = None
    join = os.path.join
    isdir = os.path.isdir
    split = os.path.split
    for name,dist in libs:
        try:
            __import__(name)
        except ImportError:
            pass
        else:
            continue
        if not workspace_dir:
            dir = split(os.path.abspath(__file__))[0]
            cdir = join(dir,dist)
            while not isdir(cdir):
                dir = split(dir)[0]
                diname = split(dir)[1]
                if diname == dist:
                    cdir = dir
                    break
                cdir = join(dir,dist)
            workspace_dir = split(cdir)[0]
        
        dist_dir = join(workspace_dir,dist)
        if isdir(dist_dir):
            sys.path.insert(0,dist_dir)
        