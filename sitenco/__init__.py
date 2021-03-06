"""
Site'N'Co
=========

Simple websites for simple projects.

"""

import os.path
import docutils.core
import docutils.writers.html4css1
import xml.etree.ElementTree as ET
from datetime import datetime
from docutils_html5 import Writer
from werkzeug.exceptions import NotFound
from flask import (
    Flask, Response, g, render_template, request, send_from_directory,
    redirect)


PROJECT_NAME = None
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(SITE_ROOT, '..', 'projects')
DOCS_PATH = os.path.join(SITE_ROOT, '..', 'docs')

from . import directives
from .cache import cache, clean_cache
from .config import Config, TOOLS


class ConfigRepository(object):
    """Configurations repository.

    Behaves like a dict of project name string -> configuration dict.

    On access, check the modification time of config files and re-read them as
    needed.

    """
    def __init__(self):
        self._cache = {}

    def __getitem__(self, project_name):
        filename = os.path.join(PATH, project_name, 'configuration.yaml')
        if not os.path.isfile(filename):
            raise KeyError
        mtime = os.path.getmtime(filename)

        if project_name in self._cache:
            old_mtime, config = self._cache[project_name]
            if old_mtime == mtime:
                return config

        config = Config(filename)
        self._cache[project_name] = mtime, config
        return config


CONFIG = ConfigRepository()

# We’re not using Flask’s static files, do not publish anything on /static.
app = Flask(__name__, static_path=None)


def _open_or_404(type_or_filename, page_name=None):
    """Return content or raise 404."""
    if type_or_filename.startswith('/'):
        filename = '%s.rst' % type_or_filename
    else:
        filename = os.path.join(
            PATH, g.project_name, type_or_filename, '%s.rst' % page_name)
    try:
        return open(filename).read()
    except IOError:
        raise NotFound


def _list_news():
    """List the content of type ``content_type``."""
    folder = os.path.join(PATH, g.project_name, "news")
    if not os.path.isdir(folder):
        raise NotFound
    filenames = {}
    for user in os.listdir(folder):
        news = os.listdir(os.path.join(folder, user))
        for filename in news:
            filenames[filename] = os.path.join(
                folder, user, os.path.splitext(filename)[0])
    for key in sorted(filenames, reverse=True):
        yield filenames[key]


def _rest_to_article(text, level=2, id_prefix='id'):
    """Convert ReST ``text`` to HTML article."""
    return docutils.core.publish_parts(
        source=text, writer=Writer(),
        settings_overrides={
            'initial_header_level': level,
            'id_prefix': id_prefix})


@app.template_filter()
def pretty_datetime(datetime_string, format_=None):
    """Convert an internal datetime string to a pretty date."""
    date = datetime.strptime(datetime_string, '%Y-%m-%d@%H:%M:%S')
    if format_ == "_iso_":
        return date.isoformat()
    return date.strftime(format_ or '%A, %B %-d %Y')


@app.before_request
def before_request():
    """Set variables before each request."""
    host_parts = request.host.split('.')
    if 'www' in host_parts:
        host_parts.remove('www')
    g.project_name = PROJECT_NAME or host_parts[0]
    g.config = CONFIG[g.project_name]
    g.variables = CONFIG[g.project_name].config_tree.copy()


@app.route('/rss/')
@cache
def rss():
    """RSS feed."""
    ordered_news = {name: _open_or_404(name) for name in _list_news()}

    tree = ET.Element('rss', {'version': '2.0'})
    channel = ET.Element('channel')
    tree.append(channel)
    title = ET.Element('title')
    title.text = '%s - %s' % (g.variables['name'], g.variables['description'])
    channel.append(title)
    description = ET.Element('description')
    description.text = u'News from %s' % g.variables['name']
    channel.append(description)
    link = ET.Element('link')
    link.text = request.host_url
    channel.append(link)

    for filename, new in sorted(ordered_news.items(), reverse=True):
        date = os.path.basename(filename)
        id_string = date
        url = "%snews#%s" % (request.host_url, id_string)
        item = ET.Element('item')
        channel.append(item)
        title = ET.Element('title')
        item.append(title)
        guid = ET.Element('guid')
        guid.text = str(hash(new))
        item.append(guid)
        pubdate = ET.Element('pubDate')
        pubdate.text = datetime.strptime(
            date, '%Y-%m-%d@%H:%M:%S').strftime('%a, %d %b %Y %H:%M:%S +0000')
        item.append(pubdate)
        link = ET.Element('link')
        link.text = url
        item.append(link)

        parts = docutils.core.publish_parts(
            source=new,
            writer=docutils.writers.html4css1.Writer(),
            settings_overrides={'initial_header_level': 2})
        description_text = parts['fragment']
        title.text = parts['title']
        description = ET.Element('description')
        description.text = description_text
        item.append(description)

    return Response(
        b'<?xml version="1.0" encoding="UTF-8" ?>\n' +
        ET.tostring(tree, 'utf-8', method='xml'),
        mimetype='application/rss+xml')


@app.route('/news/')
@cache
def news():
    """News."""
    g.variables.update({
        'page_title': 'News',
        'news': ({
            'datetime': os.path.basename(new),
            'html': _rest_to_article(
                _open_or_404(new), level=3, id_prefix=os.path.basename(new))
            ['article']} for new in _list_news())})
    return render_template('news.html.jinja2', **g.variables)


@app.route('/<folder>/<path:path>')
def static_file(folder, path):
    """Static files."""
    filenames = (
        (PATH, os.path.join(g.project_name, 'static', folder, path)),
        (SITE_ROOT, os.path.join('static', folder, path)))
    for base, filename in filenames:
        if os.path.isfile(os.path.join(base, filename)):
            return send_from_directory(base, filename)
    raise NotFound


@app.route('/docs/', defaults={'path': ''})
@app.route('/docs/<path:path>')
def sphinx_docs(path):
    """Sphinx docs."""
    tool = g.config.tools.get('sphinx')
    if not tool:
        raise NotFound
    if path.endswith('/') or not path:
        path += 'index.html'
    return send_from_directory(
        os.path.join(tool.path, 'docs', '_build', 'dirhtml'), path)


@app.route('/_update/<source_tool>', methods=['GET', 'POST'])
@clean_cache
def update(source_tool):
    """Update the tools."""
    for tool in TOOLS:
        tool_name = tool.__name__.split('.')[-1]
        if tool_name in g.config.tools and tool_name != source_tool:
            g.config.tools[tool_name].update()
    return '%s updated' % g.project_name


@app.route('/')
@app.route('/<page>/')
@cache
def default(page='home'):
    """Default page."""
    redirect_url = g.variables.get('redirects', {}).get(request.path)
    if redirect_url:
        return redirect(redirect_url)
    item = _rest_to_article(_open_or_404('pages', page))
    g.variables.update({'page': item['article'], 'page_title': item['title']})
    return render_template('page.html.jinja2', pagename=page, **g.variables)
