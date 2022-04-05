import json
from configparser import ConfigParser

from ...errors import Invalid, ParserNotFound
from ...template import Template


def get_vars(source_medium, dry_run, interactive=True):
    """
        Parse given file and copy the content to a dict of dicts.

        Also, the values are rendered with jinja2 template.

    """
    source = source_medium.root
    project_conf = source_medium.joinpath(source, "project.conf")
    if not source_medium.exists(project_conf):
        raise ParserNotFound("Config %s does not exists" % project_conf)

    config = ConfigParser()

    # This trick allows the option key to remain case-sensitive
    config.optionxform = str
    config.read_string(source_medium.read_text(project_conf))
    variables = {}

    for section in config.sections():
        section_dict = dict(config[section])
        variables[section] = section_dict

        if dry_run:
            print("Section:", section, project_conf)

        for key, val in section_dict.items():
            is_hidden = key.startswith("_") or section.startswith("_")
            _val = Template(val).render(variables)
            if interactive and not is_hidden:
                _val = question(key, _val)
            if dry_run:
                print("Choice: ", key, "=", _val)

            variables[section][key] = _val

    return variables


def question(question, defaultvalue):

    if defaultvalue.startswith("json::"):
        _json_stuff = json.loads(defaultvalue[6:])

        if isinstance(_json_stuff, list):
            return question_from_list(question, _json_stuff)
        elif isinstance(_json_stuff, str):
            return question_from_string(question, _json_stuff)
        else:
            raise NotImplementedError
    else:
        return question_from_string(question, defaultvalue)


def question_from_string(quest, ion):
    reply = input("{}? [{}]: ".format(quest, ion))
    if reply:
        return reply
    return ion


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
