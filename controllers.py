import os
import mimetypes
import werkzeug
import werkzeug.exceptions
import kraken
from kraken.site import expose, expose_template

from kalamarsite import SITE
from sitenco import SITE_ROOT, PROJECTS_PATH
from local import LOCAL
from css import css
from rss import rss


def _open_or_404(*args, **kwargs):
    """Open an item matching ``args``, or raise an 404 error."""
    try:
        return SITE.open(*args, **kwargs)
    except:
        raise werkzeug.exceptions.NotFound

def _static(environ, filename, mimetype=None):
    """Get a response wrapping the file called filename."""
    fullpath = os.path.join(SITE_ROOT, filename)
    if not os.path.isfile(fullpath):
        raise werkzeug.exceptions.NotFound
    wrapped_file = werkzeug.wrap_file(environ, open(fullpath))
    if not mimetype:
        mimetype = mimetypes.guess_type(filename)[0]
    return werkzeug.BaseResponse(
        wrapped_file, direct_passthrough=True, mimetype=mimetype)

@expose('/static/<path:path>')
def static(request, path):
    """Static part of projects."""
    filename = os.path.join(PROJECTS_PATH, LOCAL.project_name, 'static', path)
    return _static(request.environ, filename)

@expose('/src/<path:path>')
def src(request, path):
    """Commun static part of Site'n'Co for sources."""
    return _static(request.environ, os.path.join('static', 'src', path))

@expose('/css/csstyle.css')
def csstyle_stylesheet(request):
    """Style management with CSStyle."""
    return werkzeug.BaseResponse(css(), headers={'Content-Type': 'text/css'})

@expose('/css/<path:path>')
def css_static_files(request, path):
    """CSS static files."""
    filenames = (
        os.path.join(PROJECTS_PATH, LOCAL.project_name, 'static', 'css', path),
        os.path.join(SITE_ROOT, 'static', 'css', path))
    for filename in filenames:
        if os.path.isfile(filename):
            return _static(request.environ, filename)
    raise werkzeug.exceptions.NotFound

@expose('/rss')
def rss_feed(request):
    """News RSS feed."""
    return werkzeug.BaseResponse(
        rss(request.host_url), headers={'Content-Type': 'application/rss+xml'})

@expose_template('/news')
def news(request):
    """News pages."""
    news = SITE.search('news', {'project': LOCAL.project_name})
    LOCAL.variables.update({'page_title': 'News', 'news': news})
    return LOCAL.variables

@expose('/tutorials/<string:tutorial>')
def tutorial(request, tutorial):
    """Tutorial."""
    item = None
    LOCAL.variables.update({'tutorial': tutorial , 'page_title': 'Tutorials'})

    item = _open_or_404(
        'tutorial', {'project': LOCAL.project_name, 'tutorial': tutorial})
    LOCAL.variables.update(
        {'page_title': item['title'], 'tutorial': item})
    filename = os.path.join(
        PROJECTS_PATH, LOCAL.project_name, 'tutorials', '%s.html' % tutorial)
    if os.path.isfile(filename):
        return _static(request.environ, filename, 'text/html')

    response = kraken.site.TemplateResponse(
        LOCAL.site, 'tutorial', LOCAL.variables)

    with open(filename, 'w') as fd:
        fd.write(response.data)

    return response

@expose_template('/tutorials')
def tutorials(request):
    """Tutorials."""
    tutorials = SITE.search('tutorial', {'project': LOCAL.project_name})
    LOCAL.variables.update({'page_title': 'Tutorials', 'tutorials': tutorials})
    return LOCAL.variables

@expose('/<path:page>')
def default(request, page='home'):
    """Static ReST pages."""
    item = _open_or_404('page', {'project': LOCAL.project_name, 'page': page})
    LOCAL.variables.update({'page': item, 'page_title': item['title']})
    return kraken.site.TemplateResponse(LOCAL.site, 'page', LOCAL.variables)

@expose('/')
def root(request):
    """Home page."""
    return default(request)
