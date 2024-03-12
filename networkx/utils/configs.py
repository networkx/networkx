import collections
import types
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

    Once defined, configuration items may be modified, but can't be added or deleted.
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

    """

    def __new__(cls, **kwargs):
        orig_class = cls
        if cls is Config:
            # Enable the "simple" case of accepting config definition as keywords
            cls = type(
                cls.__name__,
                (cls,),
                {"__annotations__": {key: typing.Any for key in kwargs}},
            )
        cls = dataclass(eq=False, slots=True, kw_only=True, match_args=False)(cls)
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
        if key not in self.__dataclass_fields__:
            raise AttributeError(f"Invalid config name: {key!r}")
        self._check_config(key, value)
        object.__setattr__(self, key, value)

    def __delattr__(self, key):
        raise TypeError(f"Configuration items can't be deleted (can't delete {key!r}).")

    # Be a `collection.abc.Collection`
    def __contains__(self, key):
        return key in self.__dataclass_fields__

    def __iter__(self):
        return iter(self.__dataclass_fields__)

    def __len__(self):
        return len(self.__dataclass_fields__)

    def __reversed__(self):
        return reversed(self.__dataclass_fields__)

    # Add dunder methods for `collections.abc.Mapping`
    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError as err:
            raise KeyError(*err.args) from None

    def __setitem__(self, key, value):
        try:
            setattr(self, key, value)
        except AttributeError as err:
            raise KeyError(*err.args) from None

    __delitem__ = __delattr__
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

    # Make type annotations work with key and value types; e.g. Config[str, int]
    def __class_getitem__(cls, item):
        return types.GenericAlias(cls, item)


# Register, b/c `Mapping.__subclasshook__` returns `NotImplemented`
collections.abc.Mapping.register(Config)


class NetworkXConfig(Config):
    """Write me!"""

    backend_priority: list[str]
    backends: Config[str, Config]

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


# Backend configuration will be updated in backends.py
config = NetworkXConfig(
    backend_priority=[],
    backends=Config(),
)
