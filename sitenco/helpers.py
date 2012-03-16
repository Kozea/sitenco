"""
Various Helpers

"""

import docutils.core
from docutils.parsers.rst import directives, Directive

import os
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Number
import subprocess
from docutils_html5 import Writer
from flask import g
from traceback import format_exc
import pygal

ROOT = os.path.join(os.path.dirname(__file__), '..', 'projects')


class PygmentsStyle(Style):
    """Pygments style based on Solarized."""
    styles = {
        Keyword: '#b58900',
        Name: '#cb4b16',
        Comment: '#839496',
        String: '#2aa198',
        Error: '#dc322f',
        Number: '#859900'}


class Pygments(Directive):
    """Code syntax hightlighting."""
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        filename = os.path.join(ROOT, g.project_name, self.arguments[0])
        lexer_name = self.arguments[1] if len(self.arguments) > 1 else 'python'
        code = open(filename).read()
        lexer = get_lexer_by_name(lexer_name)
        formatter = HtmlFormatter(
            noclasses=True, nobackground=True, style=PygmentsStyle)
        parsed = pygments.highlight(code, lexer, formatter)
        return [docutils.nodes.raw('', parsed, format='html')]


class InlinePygments(Directive):
    """Inline code sytax highlighting."""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def run(self):
        lexer = get_lexer_by_name(self.arguments[0])
        code = u'\n'.join(self.content)
        formatter = HtmlFormatter(
            noclasses=True, nobackground=True, style=PygmentsStyle)
        parsed = pygments.highlight(code, lexer, formatter)
        return [docutils.nodes.raw('', parsed, format='html')]


class UrlGet(Directive):
    """Serve the response of a request."""
    required_arguments = 2
    optional_arguments = 0
    has_content = False

    def run(self):
        filename = os.path.join(ROOT, g.project_name, self.arguments[0])
        url = self.arguments[1]
        parts = filename.split('/')
        cwd = '/'.join(parts[:-1])
        pipe = subprocess.Popen(
            ['python', filename, url], cwd=cwd, stdout=subprocess.PIPE)
        content = pipe.communicate()[0].strip()
        retcode = pipe.poll()
        if retcode:
            content = 'An error occured %s' % '-'.join([filename, url])
        content = content.replace(
            '<html', '<html style="background-color: white"')
        content = '<iframe src="data:text/html;base64,%s">' \
            'Request Output</iframe>' % content.encode('base64')
        # Remove EOLs
        content = content.replace('\n', '')
        return [docutils.nodes.raw('', content, format='html')]


class PyResult(Directive):
    """Execute the given python file and puts its result in the document."""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        filename = os.path.join(ROOT, g.project_name, self.arguments[0])
        pipe = subprocess.Popen(['python', filename], stdout=subprocess.PIPE)
        content = pipe.communicate()[0]
        retcode = pipe.poll()
        if retcode:
            content = 'An error occured'
        content = '<pre class="script-output">%s</pre>' % content
        return [docutils.nodes.raw('', content, format='html')]


class Pygal(Directive):
    """Execute the given python file and puts its result in the document."""
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = True
    has_content = True

    def run(self):
        width, height = map(int, self.arguments) if len(
            self.arguments) == 2 else (600, 400)
        code = '\n'.join(self.content)
        locals = {'pygal': pygal}
        exec(code, {}, locals)
        chart = None
        for value in locals.values():
            if isinstance(value, pygal.graph.graph.Graph):
                chart = value
                break
        if chart == None:
            return [docutils.nodes.system_message(
                'No instance of graph found', level=3)]
        chart.disable_xml_declaration = True
        chart.config.width = width
        chart.config.height = height
        chart.explicit_size = True
        try:
            svg = chart.render()
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
        code = u'\n'.join(self.content)
        formatter = HtmlFormatter(
            noclasses=True, nobackground=True, style=PygmentsStyle)
        parsed = pygments.highlight(code, lexer, formatter)
        node_list.append(
            docutils.nodes.caption(
                '', '', docutils.nodes.raw('', parsed, format='html')))
        return [docutils.nodes.figure('', *node_list)]

directives.register_directive('pycode', Pygments)
directives.register_directive('code-block', InlinePygments)
directives.register_directive('pyexec', PyResult)
directives.register_directive('werkzeugurl', UrlGet)
directives.register_directive('pygal', Pygal)
directives.register_directive('pygal-code', PygalWithCode)


def rest_to_article(text, level=2):
    """Convert ReST ``text`` to HTML article."""
    return docutils.core.publish_parts(
        source=text, writer=Writer(),
        settings_overrides={'initial_header_level': level})
