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
        self._tools = []
        self._config_tree = yaml.load(open(path))
        for tool_module in TOOLS:
            module_tools = {}
            module_name = tool_module.__name__.split('.')[-1]
            tools = self._config_tree.get(module_name) or {}
            for name, config in tools.items():
                tool_class = getattr(tool_module, name.capitalize())
                public = self.get([module_name, name, 'public'])
                module_tools['name'] = (tool_class(public=public, **config))

            for directive_name in dir(tool_module):
                directive = getattr(tool_module, directive_name)
                if isinstance(directive, type):
                    if issubclass(directive, tool.Directive):
                        directive.tool_dict = module_tools
                        directives.register_directive(
                            directive_name.lower(), directive)

            self._tools.extend(module_tools.values())

    def get(self, folders, node=None):
        """Get the property at ``folders``."""
        node = node or self._config_tree
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

    @property
    def tools(self):
        """List of the tools defined in the configuration file."""
        return self._tools

    @property
    def config_tree(self):
        """Configuration tree taken from the yaml configuration file."""
        return self._config_tree
