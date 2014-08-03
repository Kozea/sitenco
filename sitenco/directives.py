"""
ReST directives.

"""

import docutils.core
from docutils.parsers.rst import directives, Directive

import os
import pygments
import base64
import pygal
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Number
from traceback import format_exc


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


class Pygal(Directive):
    """Execute the given python file and puts its result in the document."""
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = True
    has_content = True

    def run(self):
        width, height = map(int, self.arguments[:2]) if len(
            self.arguments) >= 2 else (600, 400)
        if len(self.arguments) == 1:
            self.render_fix = bool(self.arguments[0])
        elif len(self.arguments) == 3:
            self.render_fix = bool(self.arguments[2])
        else:
            self.render_fix = False
        self.content = list(self.content)
        content = list(self.content)
        if self.render_fix:
            content[-1] = 'rv = ' + content[-1]
        code = '\n'.join(content)
        scope = {'pygal': pygal}
        try:
            exec(code, scope)
        except Exception:
            return [docutils.nodes.system_message(
                'An exception as occured during code parsing:'
                ' \n %s' % format_exc(),
                level=3)]
        if self.render_fix:
            rv = scope['rv']
        else:
            chart = None
            for key, value in scope.items():
                if isinstance(value, pygal.ghost.Ghost):
                    chart = value
                    self.content.append(key + '.render()')
                    break
            if chart is None:
                return [docutils.nodes.system_message(
                    'No instance of graph found', level=3)]
            chart.config.width = width
            chart.config.height = height
            chart.explicit_size = True
            rv = chart.render()

        try:
            svg = (
                '<embed src="data:image/svg+xml;charset=utf-8;base64,%s" />' %
                base64.b64encode(rv).decode('utf-8')
                .replace('\n', ''))
        except Exception:
            return [docutils.nodes.system_message(
                'An exception as occured during graph generation:'
                ' \n %s' % format_exc(),
                level=3)]
        return [docutils.nodes.raw('', svg, format='html')]


class PygalWithCode(Pygal):
    width_code = True

    def run(self):
        node_list = super(PygalWithCode, self).run()
        lexer = get_lexer_by_name('python')
        code = '\n'.join(self.content)
        formatter = HtmlFormatter(
            noclasses=True, nobackground=True, style=PygmentsStyle)
        parsed = pygments.highlight(code, lexer, formatter)
        node_list.append(
            docutils.nodes.caption(
                '', '', docutils.nodes.raw('', parsed, format='html')))
        return [docutils.nodes.figure('', *node_list)]


directives.register_directive('code-block', InlinePygments)
directives.register_directive('pygal', Pygal)
directives.register_directive('pygal-code', PygalWithCode)

