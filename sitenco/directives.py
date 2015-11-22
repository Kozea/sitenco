"""
ReST directives.

"""

import docutils.core
from docutils.parsers.rst import directives, Directive

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Number


class PygmentsStyle(Style):
    """Pygments style based on Solarized."""
    styles = {
        Keyword: '#b58900',
        Name: '#cb4b16',
        Comment: '#839496',
        String: '#2aa198',
        Error: '#dc322f',
        Number: '#859900'}


class InlinePygments(Directive):
    """Inline code sytax highlighting."""
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = True

    def run(self):
        lexer = get_lexer_by_name(
            self.arguments[0] if len(self.arguments) == 1 else 'python')
        code = '\n'.join(self.content)
        formatter = HtmlFormatter(
            noclasses=True, nobackground=True, style=PygmentsStyle)
        parsed = pygments.highlight(code, lexer, formatter)
        return [docutils.nodes.raw('', parsed, format='html')]


directives.register_directive('code-block', InlinePygments)

