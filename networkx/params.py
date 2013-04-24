"""
Defines NetworkX configuration parameters.

Eventually we could support some sort of config file.  For now, it can be
updated via the dictionary API only.

"""

import warnings

__all__ = ['nxParams', 'reset_params']

### Generic validations

def validate_boolean(b):
    """Convert b to a boolean or raise a ValueError."""
    try:
        b = b.lower()
    except AttributeError:
        pass
    if b in ('t', 'y', 'yes', 'on', 'true', '1', 1, True): return True
    elif b in ('f', 'n', 'no', 'off', 'false', '0', 0, False): return False
    else:
        raise ValueError('Could not convert {0!r} to boolean'.format(b))

def validate_float(s):
    """Convert s to float or raise a ValueError."""
    try:
        return float(s)
    except ValueError:
        raise ValueError('Could not convert {0!r} to float'.format(s))

def validate_choice(s, choices):
    try:
        s = s.lower()
    except AttributeError:
        pass
    if s not in choices:
        raise ValueError("{0!r} is an invalid specification.".format(s))
    else:
        return s

### Specific validations

def validate_pydot_show(s):
    choices = ['ipynb', 'external', 'none']
    return validate_choice(s, choices)


### The main parameter class

class NetworkXParams(dict):
    """
    A dictionary including validation, representing NetworkX parameters.

    """

    def __init__(self, *args, **kwargs):
        # A dictionary relating params to validators.
        self.validate = dict([(key, converter) for key, (default, converter) \
                              in defaultParams.iteritems()])

        dict.__init__(self, *args, **kwargs)

    def _deprecation_check(self, param):
        """
        Raise warning if param is deprecated.

        Return the param to use. This is the alternative parameter if available,
        otherwise it is the original parameter.

        """
        if param in deprecatedParams:
            alt = deprecatedParams[param]
            if alt is None:
                msg = "{0!r} is deprecated. There is no replacement."
                msg = msg.format(key)
            else:
                msg = "{0!r} is deprecated. Use {1!r} instead."
                msg = msg.format(key, alt)
                param = alt

            warnings.warn(msg, DeprecationWarning, stacklevel=2)

        if param not in self.validate:
            msg = '{0!r} is not a valid NetworkX parameter. '.format(key)
            msg += 'See nxParams.keys() for a list of valid parameters.'
            raise KeyError(msg)

        return param

    def __setitem__(self, key, val):
        key = self._deprecation_check(key)
        cval = self.validate[key](val)
        dict.__setitem__(self, key, cval)

    def __getitem__(self, key):
        key = self._deprecation_check(key)
        return dict.__getitem__(self, key)

def reset_params():
    """
    Restore rcParams to defaults for NetworkX.

    """
    # This modifies the global parameters.
    nxParams.update(nxParamsDefault)

def set_params(filename=None):
    """
    Return the default params, after updating from the .nxrc file.

    """
    # Currently, we don't support a config file.
    # For now, just return a NetworkXParams instance with the default values.
    ret =  NetworkXParams([ (key, tup[0]) for key, tup in defaultParams.items()])
    return ret


### Globals



### TODO:  key -> (value, validator, info_string)
defaultParams = {
    # parameter : (default value, validator)
    'pydot_show': ('external', validate_pydot_show),
}

### Dictionary relating deprecated parameter names to new names.
deprecatedParams = {
    # old parameter : new parameter, (use None if no new parameter)
}

### This is what will be used by NetworkX modules.
nxParams = set_params()
nxParamsDefault = NetworkXParams([(key, tup[0]) \
                                for key, tup in defaultParams.items()])

