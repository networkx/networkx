import collections
import os
import typing
from dataclasses import dataclass

__all__ = ["Config", "config"]


@dataclass(init=False, eq=False, slots=True, kw_only=True, match_args=False)
class Config:
    """The base class for NetworkX configuration.

    There are two ways to use this to create configurations. The first is to
    simply pass the initial configuration as keyword arguments to ``Config``:

    >>> cfg = Config(eggs=1, spam=5)
    >>> cfg
    Config(eggs=1, spam=5)

    The second--and preferred--way is to subclass ``Config`` with docs and annotations.

    >>> class MyConfig(Config):
    ...     '''Breakfast!'''
    ...
    ...     eggs: int
    ...     spam: int
    ...
    ...     def _check_config(self, key, value):
    ...         assert isinstance(value, int) and value >= 0
    >>> cfg = MyConfig(eggs=1, spam=5)

    Once defined, config items may be modified, but can't be added or deleted by default.
    ``Config`` is a ``Mapping``, and can get and set configs via attributes or brackets:

    >>> cfg.eggs = 2
    >>> cfg.eggs
    2
    >>> cfg["spam"] = 42
    >>> cfg["spam"]
    42

    Subclasses may also define ``_check_config`` (as done in the example above)
    to ensure the value being assigned is valid:

    >>> cfg.spam = -1
    Traceback (most recent call last):
        ...
    AssertionError

    If a more flexible configuration object is needed that allows adding and deleting
    configurations, then pass ``strict=False`` when defining the subclass:

    >>> class FlexibleConfig(Config, strict=False):
    ...     default_greeting: str = "Hello"
    >>> flexcfg = FlexibleConfig()
    >>> flexcfg.name = "Mr. Anderson"
    >>> flexcfg
    FlexibleConfig(default_greeting='Hello', name='Mr. Anderson')
    """

    def __init_subclass__(cls, strict=True):
        cls._strict = strict

    def __new__(cls, **kwargs):
        orig_class = cls
        if cls is Config:
            # Enable the "simple" case of accepting config definition as keywords
            cls = type(
                cls.__name__,
                (cls,),
                {"__annotations__": {key: typing.Any for key in kwargs}},
            )
        cls = dataclass(
            eq=False,
            repr=cls._strict,
            slots=cls._strict,
            kw_only=True,
            match_args=False,
        )(cls)
        if not cls._strict:
            cls.__repr__ = _flexible_repr
        cls._orig_class = orig_class  # Save original class so we can pickle
        instance = object.__new__(cls)
        instance.__init__(**kwargs)
        return instance

    def _check_config(self, key, value):
        """Check whether config value is valid. This is useful for subclasses."""

    # Control behavior of attributes
    def __dir__(self):
        return self.__dataclass_fields__.keys()

    def __setattr__(self, key, value):
        if self._strict and key not in self.__dataclass_fields__:
            raise AttributeError(f"Invalid config name: {key!r}")
        self._check_config(key, value)
        object.__setattr__(self, key, value)

    def __delattr__(self, key):
        if self._strict:
            raise TypeError(
                f"Configuration items can't be deleted (can't delete {key!r})."
            )
        object.__delattr__(self, key)

    # Be a `collection.abc.Collection`
    def __contains__(self, key):
        return (
            key in self.__dataclass_fields__ if self._strict else key in self.__dict__
        )

    def __iter__(self):
        return iter(self.__dataclass_fields__ if self._strict else self.__dict__)

    def __len__(self):
        return len(self.__dataclass_fields__ if self._strict else self.__dict__)

    def __reversed__(self):
        return reversed(self.__dataclass_fields__ if self._strict else self.__dict__)

    # Add dunder methods for `collections.abc.Mapping`
    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError as err:
            raise KeyError(*err.args) from None

    def __setitem__(self, key, value):
        try:
            self.__setattr__(key, value)
        except AttributeError as err:
            raise KeyError(*err.args) from None

    def __delitem__(self, key):
        try:
            self.__delattr__(key)
        except AttributeError as err:
            raise KeyError(*err.args) from None

    _ipython_key_completions_ = __dir__  # config["<TAB>

    # Go ahead and make it a `collections.abc.Mapping`
    def get(self, key, default=None):
        return getattr(self, key, default)

    def items(self):
        return collections.abc.ItemsView(self)

    def keys(self):
        return collections.abc.KeysView(self)

    def values(self):
        return collections.abc.ValuesView(self)

    # dataclass can define __eq__ for us, but do it here so it works after pickling
    def __eq__(self, other):
        if not isinstance(other, Config):
            return NotImplemented
        return self._orig_class == other._orig_class and self.items() == other.items()

    # Make pickle work
    def __reduce__(self):
        return self._deserialize, (self._orig_class, dict(self))

    @staticmethod
    def _deserialize(cls, kwargs):
        return cls(**kwargs)


def _flexible_repr(self):
    return (
        f"{self.__class__.__qualname__}("
        + ", ".join(f"{key}={val!r}" for key, val in self.__dict__.items())
        + ")"
    )


# Register, b/c `Mapping.__subclasshook__` returns `NotImplemented`
collections.abc.Mapping.register(Config)


class NetworkXConfig(Config):
    """Configuration for NetworkX that controls behaviors such as how to use backends.

    Attribute and bracket notation are supported for getting and setting configurations:

    >>> nx.config.backend_priority == nx.config["backend_priority"]
    True

    Parameters
    ----------
    backend_priority : list of backend names
        Enable automatic conversion of graphs to backend graphs for algorithms
        implemented by the backend. Priority is given to backends listed earlier.
        Default is empty list.

    backends : Config mapping of backend names to backend Config
        The keys of the Config mapping are names of all installed NetworkX backends,
        and the values are their configurations as Config mappings.

    cache_converted_graphs : bool
        If True, then save converted graphs to the cache of the input graph. Graph
        conversion may occur when automatically using a backend from `backend_priority`
        or when using the `backend=` keyword argument to a function call. Caching can
        improve performance by avoiding repeated conversions, but it uses more memory.
        Care should be taken to not manually mutate a graph that has cached graphs; for
        example, ``G[u][v][k] = val`` changes the graph, but does not clear the cache.
        Using methods such as ``G.add_edge(u, v, weight=val)`` will clear the cache to
        keep it consistent. ``G.__networkx_cache__.clear()`` manually clears the cache.
        Default is False.

    Notes
    -----
    Environment variables may be used to control some default configurations:

    - NETWORKX_BACKEND_PRIORITY: set `backend_priority` from comma-separated names.
    - NETWORKX_CACHE_CONVERTED_GRAPHS: set `cache_converted_graphs` to True if nonempty.

    This is a global configuration. Use with caution when using from multiple threads.
    """

    backend_priority: list[str]
    backends: Config
    cache_converted_graphs: bool

    def _check_config(self, key, value):
        from .backends import backends

        if key == "backend_priority":
            if not (isinstance(value, list) and all(isinstance(x, str) for x in value)):
                raise TypeError(
                    f"{key!r} config must be a list of backend names; got {value!r}"
                )
            if missing := {x for x in value if x not in backends}:
                missing = ", ".join(map(repr, sorted(missing)))
                raise ValueError(f"Unknown backend when setting {key!r}: {missing}")
        elif key == "backends":
            if not (
                isinstance(value, Config)
                and all(isinstance(key, str) for key in value)
                and all(isinstance(val, Config) for val in value.values())
            ):
                raise TypeError(
                    f"{key!r} config must be a Config of backend configs; got {value!r}"
                )
            if missing := {x for x in value if x not in backends}:
                missing = ", ".join(map(repr, sorted(missing)))
                raise ValueError(f"Unknown backend when setting {key!r}: {missing}")
        elif key == "cache_converted_graphs":
            if not isinstance(value, bool):
                raise TypeError(f"{key!r} config must be True or False; got {value!r}")


# Backend configuration will be updated in backends.py
config = NetworkXConfig(
    backend_priority=[],
    backends=Config(),
    cache_converted_graphs=bool(os.environ.get("NETWORKX_CACHE_CONVERTED_GRAPHS", "")),
)
