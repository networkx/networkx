from networkx.external.decorator import decorator
from networkx.utils import is_string_like
from collections import defaultdict
from os.path import splitext
import networkx as nx


def require(*packages):
    """ Decorator to check whether specific packages can be imported
    if not throw a NetworkXError

    Parameters
    ----------
    packages : container of strings
      Container of strings to try and import

    Returns
    -------
    _require : function
      Same function as decorator is placed on.

    Raises
    ------
    NetworkXError
      If any of the packages cannot be imported

    Examples
    --------
    @require('scipy')
    def sp_function():
        import scipy
        pass

    @require('numpy','scipy')
    def sp_np_function():
        import numpy
        import scipy
        pass
    
    """
    @decorator
    def _require(f,*args,**kwargs):
        for package in reversed(packages):
            try:
                __import__(package)
            except:
                raise nx.NetworkXError("%s requires %s"%(f.__name__,package))
        return f(*args,**kwargs)
    return _require


def _open_gz(path,mode):
    import gzip
    return gzip.open(path,mode=mode)

def _open_bz2(path,mode):
    import bz2
    return bz2.BZ2File(path,mode=mode)

#clever way to write new ways of opening files
#if you want to add a new way for a new extension
#just add an function that takes a path string and
# a mode and add the extension to _dispatch_dict
# 
_dispatch_dict = defaultdict(lambda : open)
_dispatch_dict['.gz'] = _open_gz
_dispatch_dict['.bz2'] = _open_bz2
_dispatch_dict['.gzip'] = _open_gz    


def open_file(path_arg, mode='r'):
    """ Decorator to ensure clean opening and closing of files

    Parameters
    ----------
    path_arg : int
      Location of the path argument in args
    mode : str
      String for opening mode

    Returns
    -------
    _open_file : function
      function which cleanly executes the io

    Examples
    --------
    @open_file(0,'r')
    def read_function(pathname):
        pass

    @open_file(1,'w')
    def write_function(G,pathname):
        pass
    """
    # Some special functions to unzip stuff
    # if we fail try good old open
    # If you want to write new ones
    @decorator
    def _open_file(func,*args,**kwargs):
        try:
            path = args[path_arg]
        except IndexError:
            raise nx.NetworkXError("path could not be found in ",
                                   "args, maybe a developer put the wrong",
                                   "Index in")
        
        str_flag = False
        if is_string_like(path):
            ext = splitext(path)[1]
            fh = _dispatch_dict[ext](path,mode=mode)
            str_flag = True
        elif hasattr(path, 'read'):
            fh = path
        else:
            raise ValueError('path must be a string or file handle')
        try:
            l_args = list(args)
            l_args[path_arg] = fh
            args = tuple(l_args)
        except: # this should never happen, EVER
            raise nx.NetworkXError("Couldn't replace path_arg",
                                   "contact NetworkX Dev team")
        try:
            result = func(*args,**kwargs)
        finally:
            if str_flag:
                fh.close()
        return result
    
    return _open_file
