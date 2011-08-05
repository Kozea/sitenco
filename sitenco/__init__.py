# coding: utf8
# pylint: disable=C0103

"""
Site'N'Co
=========

Simple websites for simple projects.

"""

import os.path
import csstyle
import docutils
import xml.etree.ElementTree as ET
from datetime import datetime
from kalamar.access_point import NotOneMatchingItem
from werkzeug.exceptions import NotFound
from flask import \
    Flask, Response, g, render_template, request, send_from_directory, redirect

from . import kalamarsite
from .helpers import rest_to_article
from .config import Config


PROJECT_NAME = None
SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(SITE_ROOT, '..', 'projects')
SITE = kalamarsite.create_site(PATH)


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
app = Flask(__name__, static_path='/nonexistent')


def _open_or_404(access_point, condition):
    """Return an item or raise 404."""
    condition['project'] = g.project_name
    try:
        return SITE.open(access_point, condition)
    except NotOneMatchingItem:
        raise NotFound


@app.template_filter()
def pretty_datetime(datetime_string):
    """Convert an internal datetime string to a pretty date."""
    return datetime.strptime(
        datetime_string, '%Y-%m-%d@%H:%M:%S').strftime('%A, %B %-d %Y')


@app.before_request
def before_request():
    """Set variables before each request."""
    g.project_name = PROJECT_NAME or request.host.split('.')[-2]
    g.variables = CONFIG[g.project_name].copy()


@app.route('/css/csstyle.css')
def csstyle_stylesheet():
    """CSS stylesheet created by CSStyle."""
    local_filename = os.path.join('static', 'css', 'style.css')
    filenames = (
        os.path.join(SITE_ROOT, local_filename),
        os.path.join(PATH, g.project_name, local_filename))

    text = '/* Generated by CSStyle */\n\n'

    for filename in filenames:
        text += open(filename).read()

    for engine in csstyle.BROWSERS:
        browser_parser = getattr(csstyle, engine)
        parser = csstyle.Parser(filenames)
        text += '\n\n/* CSS for %s */\n\n' % engine
        text += repr(browser_parser.transform(parser, keep_existant=False))

    return Response(text, mimetype='text/css')


@app.route('/rss')
def rss():
    """RSS feed."""
    news_items = SITE.search('news', {'project': g.project_name})
    ordered_news = {}
    for new in news_items:
        ordered_news[new['datetime']] = new

    tree = ET.Element('rss', {'version': '2.0'})
    channel = ET.Element('channel')
    tree.append(channel)
    title = ET.Element('title')
    title.text = '%s - %s' % (
        g.variables['name'], g.variables['description'])
    channel.append(title)
    description = ET.Element('description')
    description.text = u'News from %s' % g.variables['name']
    channel.append(description)
    link = ET.Element('link')
    link.text = request.host_url
    channel.append(link)

    for date, new in sorted(ordered_news.items(), reverse=True):
        id_string = new['datetime']
        url = "%snews#%s" % (request.host_url, id_string)
        item = ET.Element('item')
        channel.append(item)
        title = ET.Element('title')
        title.text = new['title']
        item.append(title)
        guid = ET.Element('guid')
        guid.text = str(hash(new))
        item.append(guid)
        date = ET.Element('pubDate')
        date.text = datetime.strptime(
            new['datetime'], '%Y-%m-%d@%H:%M:%S').strftime(
            '%a, %d %b %Y %H:%M:%S +0000')
        item.append(date)
        link = ET.Element('link')
        link.text = url
        item.append(link)

        parts = docutils.core.publish_parts(
            source=new['content'].read(),
            writer=docutils.writers.html4css1.Writer(),
            settings_overrides={'initial_header_level': 2, 'doctitle_xform': 0})
        description_text = parts['fragment']
        description = ET.Element('description')
        description.text = description_text
        item.append(description)

    return Response(ET.tostring(tree, 'utf-8'), mimetype='application/rss+xml')


@app.route('/news')
def news():
    """News."""
    news_items = list(SITE.search('news', {'project': g.project_name}))
    for item in news_items:
        item.html = rest_to_article(item, level=4)
    g.variables.update({'page_title': 'News', 'news': news_items})
    return render_template('news.html.jinja2', **g.variables)


@app.route('/tutorials/<string:tuto>')
def tutorial(tuto):
    """Tutorial."""
    item = _open_or_404('tutorial', {'tutorial': tuto})
    item.html = rest_to_article(item)
    filename = os.path.join(
        g.project_name, 'tutorials', '%s.html' % tuto)
    if os.path.isfile(os.path.join(PATH, filename)):
        return send_from_directory(PATH, filename)

    g.variables.update({'page_title': item['title'], 'tutorial': item})
    response = render_template('tutorial.html.jinja2', **g.variables)

    with open(os.path.join(PATH, filename), 'w') as stream:
        stream.write(response)

    return response


@app.route('/tutorials')
def tutorials():
    """Tutorials."""
    tutorials_items = SITE.search('tutorial', {'project': g.project_name})
    g.variables.update(
        {'page_title': 'Tutorials', 'tutorials': tutorials_items})
    return render_template('tutorials.html.jinja2', **g.variables)


@app.route('/tutorials/')
def tutorials_slash():
    return redirect('/tutorials')


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


@app.route('/')
@app.route('/<page>')
def default(page='home'):
    """Default page."""
    item = _open_or_404('page', {'page': page})
    item.html = rest_to_article(item)
    g.variables.update({'page': item, 'page_title': item['title']})
    return render_template('page.html.jinja2', **g.variables)
