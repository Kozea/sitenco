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
import base64
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
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = True

    def run(self):
        lexer = get_lexer_by_name(self.arguments[0]
                                  if len(self.arguments) == 1 else 'python')
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
            'Request Output</iframe>' % base64.b64encode(content)
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
        locals = {'pygal': pygal}
        try:
            exec(code, {}, locals)
        except Exception:
            return [docutils.nodes.system_message(
                'An exception as occured during code parsing:'
                ' \n %s' % format_exc(),
                level=3)]
        if self.render_fix:
            rv = locals['rv']
        else:
            chart = None
            for key, value in locals.items():
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
                '<embed src="data:image/svg+xml;charset=utf-8;base64,%s" />'
            ) % base64.b64encode(rv).decode('utf-8').replace('\n', '')
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
directives.register_directive('pygal-sparkline', PygalWithCode)


def rest_to_article(text, level=2, id_prefix='id'):
    """Convert ReST ``text`` to HTML article."""
    return docutils.core.publish_parts(
        source=text, writer=Writer(),
        settings_overrides={
            'initial_header_level': level,
            'id_prefix': id_prefix})
