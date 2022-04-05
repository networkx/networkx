import mimetypes

from jinja2 import Environment

Template = Environment(extensions=["jinja2_time.TimeExtension"]).from_string

mimetypes.init()

binary_suffixes = [k for k, v in mimetypes.types_map.items() if v.startswith("image")]

root_exclude = (".*",)
