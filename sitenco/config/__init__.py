"""
Module managing the projects configuration files.

"""

import yaml
from docutils.parsers.rst import directives

from . import tool, vcs

TOOLS = [vcs]


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
            tool_type = tool_type.strip()
            tool_name = tool_name.strip(' )')
            self.config_tree[tool_type] = self.config_tree.pop(item)

            if tool_type in tool_types:
                tool_module = tool_types[tool_type]
                tool_class = getattr(tool_module, tool_name.capitalize())
                try:
                    tool_instance = tool_class(**self.config_tree[tool_type])
                except:
                    print('Support for %s is disabled' % tool_type)
                    continue
                self.tools[tool_type] = tool_instance

                for directive_name in dir(tool_module):
                    directive = getattr(tool_module, directive_name)
                    if isinstance(directive, type):
                        if issubclass(directive, tool.Directive):
                            directive.tool = tool_instance
                            directives.register_directive(
                                directive_name.lower(), directive)

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
