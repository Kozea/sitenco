import os
import kalamar.site
from kalamar.access_point.unicode_stream import UnicodeStream
from kalamar.access_point.filesystem import FileSystem

from sitenco import PROJECTS_PATH

page = UnicodeStream(
    FileSystem(
        PROJECTS_PATH, r'(.*)/pages/(.*)\.rst', ('project', 'page')),
    'content', 'utf-8')
news = UnicodeStream(
    FileSystem(
        PROJECTS_PATH, r'(.*)/news/(.*)/(.*)\.rst',
        ('project', 'writer', 'datetime')),
    'content', 'utf-8')
tutorial = UnicodeStream(
    FileSystem(
        PROJECTS_PATH, r'(.*)/tutorials/(.*)\.rst', ('project', 'tutorial')),
    'content', 'utf-8')
                     
SITE = kalamar.site.Site()
SITE.register('page', page)
SITE.register('news', news)
SITE.register('tutorial', tutorial)
