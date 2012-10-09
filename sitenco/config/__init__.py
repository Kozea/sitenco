"""
Module managing the projects configuration files.

"""

import yaml
from docutils.parsers.rst import directives, roles

from . import (
    tool, bug_tracker, code_browser, continuous_integration, mailing_list,
    project, vcs, sphinx)

TOOLS = [
    vcs, project, code_browser, bug_tracker, continuous_integration,
    mailing_list, sphinx]


def role_generator(role):
    """Closure function returning a role function."""
    return lambda *args, **kwargs: role.run(*args, **kwargs)


class Config(object):
    """Project configuration."""
    def __init__(self, path):
        """Parse the configuration file at ``path``."""
        self.tools = {}
        self.config_tree = yaml.load(open(path))

        tool_types = {
            tool_module.__name__.split('.')[-1]: tool_module
            for tool_module in TOOLS}

        for item in self.config_tree:
            if '(' not in item:
                continue

            tool_type, tool_name = item.split('(')
            tool_type = tool_type.strip().replace(' ', '_')
            tool_name = tool_name.strip(' )')
            self.config_tree[tool_type] = self.config_tree.pop(item)

            if tool_type in tool_types:
                tool_module = tool_types[tool_type]
                tool_class = getattr(tool_module, tool_name.capitalize())

                for prop in self.config_tree[tool_type]:
                    if ' ' in prop:
                        new_prop = prop.replace(' ', '_')
                        values = self.config_tree[tool_type].pop(prop)
                        self.config_tree[tool_type][new_prop] = values

                try:
                    tool_instance = tool_class(**self.config_tree[tool_type])
                except Exception as exception:
                    print('Support for %s is disabled' % tool_type)
                    print(exception)
                    continue
                self.tools[tool_type] = tool_instance

                for class_name in dir(tool_module):
                    cls = getattr(tool_module, class_name)
                    if isinstance(cls, type):
                        if issubclass(cls, tool.Directive) and \
                               cls != tool.Directive:
                            directives.register_directive(
                                class_name.lower(), cls)
                        elif issubclass(cls, tool.Role) and cls != tool.Role:
                            roles.register_canonical_role(
                                class_name.lower(), role_generator(cls()))

    def get(self, folders, node=None):
        """Get the property at ``folders``."""
        node = node or self.config_tree
        if folders:
            folder = folders.pop(0)
            if folder in node:
                node = node.get(folder)
                if folders:
                    value = self.get(folders, node)
                    if value != None:
                        return value
                else:
                    return node
            if folders:
                folders.insert(0, folder)
                folders.pop(-2)
                return self.get(folders)
