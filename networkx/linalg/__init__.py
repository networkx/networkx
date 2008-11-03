
# need numpy for spectrum
try:
    from spectrum import *
    __all__ = spectrum.__all__
except ImportError:
    pass
