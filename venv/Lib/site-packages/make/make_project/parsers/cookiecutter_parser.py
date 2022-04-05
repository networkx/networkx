import json

from ...errors import Invalid, ParserNotFound
from ...template import Template
from .json_parser import question, question_from_list, question_from_string


def get_vars(source_medium, dry_run, interactive=True):
    """
        Parse given file and copy the content to a dict of dicts.

        Also, the values are rendered with jinja2 template.

    """
    source = source_medium.root
    project_conf = source_medium.joinpath(source, "cookiecutter.json")
    if not source_medium.exists(project_conf):
        raise ParserNotFound("Config %s does not exists" % project_conf)

    variables = {}
    section_dict = json.loads(source_medium.read_text(project_conf))

    if not isinstance(section_dict, dict):
        raise Invalid("root object have to be of type dict")

    variables["cookiecutter"] = section_dict

    for key, val in section_dict.items():
        if isinstance(val, str):
            val = Template(val).render(variables)
        if interactive:
            val = question(key, val)
        if dry_run:
            print("Choice: ", key, "=", repr(val))

        section_dict[key] = val

    return variables
