"""
Various Helpers

"""

import docutils.core
import docutils.writers.html4css1
from docutils.parsers.rst import directives, Directive

import datetime
import os
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import subprocess
from xml.etree import ElementTree

ROOT = os.path.dirname(__file__)


class Pygments(Directive):
    """Python code syntax hightlighting."""
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    def run(self):
        filename = os.path.join(ROOT, self.arguments[0])
        lexer_name = self.arguments[1] if len(self.arguments) > 1 else 'python'
        code = open(filename).read()
        lexer = get_lexer_by_name(lexer_name)
        formatter = HtmlFormatter(noclasses=True)
        parsed = pygments.highlight(code, lexer, formatter)
        return [docutils.nodes.raw('', parsed, format='html')]

class InlinePygments(Directive):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def run(self):
        lexer = get_lexer_by_name(self.arguments[0])
        code = u'\n'.join(self.content)
        formatter = HtmlFormatter(noclasses=True)
        parsed = pygments.highlight(code, lexer, formatter)
        return [docutils.nodes.raw('', parsed, format='html')]


class UrlGet(Directive):

    required_arguments = 2
    optional_arguments = 0
    has_content = False

    def run(self):
        filename = os.path.join(ROOT, self.arguments[0])
        url = self.arguments[1]
        parts =  filename.split('/')
        cwd = '/'.join(parts[:-1])
        filename = parts[-1]
        pipe = subprocess.Popen(['python', filename, url],
                cwd=cwd, stdout=subprocess.PIPE)
        content = pipe.communicate()[0].strip()
        retcode = pipe.poll()
        if retcode:
            content = 'An error occured'
        content = '<iframe src="data:text/html;base64,%s">grou?</iframe>' % content.encode('base64')
        return [docutils.nodes.raw('', content, format='html')]






class PyResult(Directive):
    """Execute the given python file and puts its result in the document."""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = False

    def run(self):
        filename = os.path.join(ROOT, self.arguments[0])
        pipe = subprocess.Popen(['python', filename], stdout=subprocess.PIPE)
        content = pipe.communicate()[0]
        retcode = pipe.poll()
        if retcode:
            content = 'An error occured'
        content = '<pre class="script-output">%s</pre>' % content
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('pycode', Pygments)
directives.register_directive('code-block', InlinePygments)
directives.register_directive('pyexec', PyResult)
directives.register_directive('werkzeugurl', UrlGet)


def rest_to_article(item, level=3):
    """Convert ``item`` to HTML article."""
    parts = docutils.core.publish_parts(
        source=item['content'],
        writer=docutils.writers.html4css1.Writer(),
        settings_overrides={'initial_header_level': level})

    # Post-production modification of generated document
    text = parts['html_body']
    # Escaping non-breaking spaces is a strange behavior in docutils, a TODO
    # exists in docutils.writers.html4css1.HTMLTranslator.encode. ElementTree
    # does not like &nbsp; so we change it by the real unicode chacarter.
    text = text.replace('&nbsp;', u'\xa0')
    tree = ElementTree.fromstring(text.encode('utf-8'))
    for element in tree.getiterator():
        if element.tag == 'div' and element.get('class') == 'document':
            element.tag = 'article'
        elif element.tag == 'tt':
            element.tag = 'code'
        elif element.tag == 'tbody':
            if 'valign' in element.attrib:
                del element.attrib['valign']
        elif element.tag == 'div' and element.get('class') == 'section':
            element.tag = 'section'
        elif element.tag == 'h1' and element.get('class') == 'title':
            element.tag = 'h%i' % (level - 1)

        for attrib in ('frame', 'rules', 'border', 'width', 'valign'):
            if attrib in element.attrib:
                del element.attrib[attrib]
    return ElementTree.tostring(tree).replace('@', u'&#64;')



def pretty_datetime(datetime_string):
    return datetime.datetime.strptime(
        datetime_string,'%Y-%m-%d@%H:%M:%S').strftime('%A, %B %-d %Y')
