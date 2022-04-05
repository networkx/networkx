import json

from ...errors import Invalid, ParserNotFound
from ...template import Template


def get_vars(source_medium, dry_run, interactive=True):
    """
        Parse given file and copy the content to a dict of dicts.

        Also, the values are rendered with jinja2 template.

    """

    source = source_medium.root
    project_conf = source_medium.joinpath(source, "project.json")
    if not source_medium.exists(project_conf):
        raise ParserNotFound("Config %s does not exists" % project_conf)

    variables = json.loads(source_medium.read_text(project_conf))

    if not isinstance(variables, dict):
        raise Invalid("root object have to be of type dict")

    for section, section_dict in variables.items():

        if not isinstance(section_dict, dict):
            raise Invalid("section '{}' have to be of type dict".format(section))

        if dry_run:
            print("Section:", section, project_conf)

        for key, val in section_dict.items():
            is_hidden = key.startswith("_") or section.startswith("_")
            if isinstance(val, str):
                val = Template(val).render(variables)
            if interactive and not is_hidden:
                val = question(key, val)
            if dry_run:
                print("Choice: ", key, "=", val)

            variables[section][key] = val

    return variables


def question(question, defaultvalue):

    if isinstance(defaultvalue, list):
        return question_from_list(question, defaultvalue)
    elif isinstance(defaultvalue, (str, bool, float, int)):
        return question_from_string(question, defaultvalue)
    else:
        raise NotImplementedError


def question_from_string(quest, ion):
    vtype = type(ion)
    reply = input("{}? [{}]: ".format(quest, str(ion)))
    if reply:
        if vtype is bool:
            return _safe_bool(reply)
        return vtype(reply)
    return ion


def _safe_bool(boolstr):
    _bool = boolstr.lower()
    if _bool in ("1", "on", "t", "true", "yes", "y") or _bool.startswith("true"):
        return True
    return False


def question_from_list(question, choices):
    size = len(choices)
    names = "\n".join(["{}) {}".format(i + 1, e) for i, e in enumerate(choices)])
    numbers = "([1], {})".format(", ".join(map(str, range(2, size + 1))))

    res = input(
        "{}? Options:\n{}\nChoose an option {}: ".format(question, names, numbers)
    )
    ires = int(res or 1)
    if 0 < ires <= size:
        return choices[ires - 1]
    else:
        raise Invalid("Invalid option")
