"""
****
YAML
****
Read and write NetworkX graphs in YAML format.

"YAML is a data serialization format designed for human readability
and interaction with scripting languages."
See http://www.yaml.org for documentation.

Format
------
http://pyyaml.org/wiki/PyYAML

"""


def __getattr__(name):
    """Remove functions and provide informative error messages."""
    if name == "read_yaml":
        raise AttributeError(
            "\nread_yaml has been removed from NetworkX, please use `yaml`\n"
            "directly:\n\n"
            "    ``yaml.load(path, Loader=yaml.Loader)``"
        )
    if name == "write_yaml":
        raise AttributeError(
            "\nwrite_yaml has been removed from NetworkX, please use `yaml`\n"
            "directly:\n\n"
            "    ``yaml.dump(G_to_be_yaml, path_for_yaml_output, **kwds)``"
        )
    raise AttributeError(f"module {__name__} has no attribute {name}")
