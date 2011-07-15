from networkx.external.decorator import decorator

def require(*packages):
    @decorator
    def _require(f,*args,**kwargs):
        for package in packages:
            try:
                __import__(package)
            except:
                raise nx.NetworkXError("%s requires %s"%(f.__name__,package))
        return f(*args,**kwargs)
    return _require


def clean_io(open_for='rw'):
    @decorator
    def _clean_io(func,path,*args,**kwargs):
        if is_string_like(path):
            fh = open(path,open_for)
        else:
            fh = path
        result = func(fh,*args,**kwargs)
        fh.close()
        return result
    return _clean_io
