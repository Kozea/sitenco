"""
Kalamar Access Points

"""

import kalamar.site
from kalamar.access_point.cache import Cache
from kalamar.access_point.xml.rest import Rest, RestProperty, TITLE
from kalamar.access_point.filesystem import FileSystem


def create_site(path):
    """Create the Kalamar site"""
    page = Rest(
        FileSystem(
            path, r'([^\._]*)/pages/(.*)\.rst', ('project', 'page')),
        [('title', RestProperty(unicode, TITLE))], 'content')
    news = Rest(
        FileSystem(
            path, r'([^\._]*)/news/(.*)/(.*)\.rst',
            ('project', 'writer', 'datetime')),
        [('title', RestProperty(unicode, TITLE))], 'content')
    tutorial = Cache(
        Rest(
            FileSystem(
                path,
                r'([^\._]*)/tutorials/(.*)\.rst', ('project', 'tutorial')),
            [('title', RestProperty(unicode, TITLE)),
             ('abstract', RestProperty(unicode, '//topic/paragraph'))],
            'content'))

    site = kalamar.site.Site()
    site.register('page', page)
    site.register('news', news)
    site.register('tutorial', tutorial)
    return site
