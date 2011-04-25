import os
import kalamar.site
from kalamar.access_point.cache import Cache
from kalamar.access_point.xml.rest import Rest, RestProperty, TITLE
from kalamar.access_point.filesystem import FileSystem

from sitenco import PROJECTS_PATH

page = Rest(
        FileSystem(
            PROJECTS_PATH, r'([a-z]*)/pages/(.*)\.rst', ('project', 'page')),
        [('title', RestProperty(unicode, TITLE))], 'content')
news = Rest(
    FileSystem(
        PROJECTS_PATH, r'([a-z]*)/news/(.*)/(.*)\.rst',
        ('project', 'writer', 'datetime')),
    [('title', RestProperty(unicode, TITLE))], 'content')
tutorial = Cache(
    Rest(
        FileSystem(
            PROJECTS_PATH,
            r'([a-z]*)/tutorials/(.*)\.rst', ('project', 'tutorial')),
        [('title', RestProperty(unicode, TITLE)),
         ('abstract', RestProperty(unicode, '//topic/paragraph'))], 'content'))
                     
SITE = kalamar.site.Site()
SITE.register('page', page)
SITE.register('news', news)
SITE.register('tutorial', tutorial)
