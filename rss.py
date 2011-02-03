import datetime
import docutils.core
import xml.etree.ElementTree as ET

from kalamarsite import SITE
from local import LOCAL


def rss(host_url):
    news = SITE.search('news', {'project': LOCAL.project_name})
    ordered_news = {}
    for new in news:
        ordered_news[new['datetime']] = new

    tree = ET.Element('rss', {'version': '2.0'})
    channel = ET.Element('channel')
    tree.append(channel)
    title = ET.Element('title')
    title.text = LOCAL.variables['title']
    channel.append(title)
    description = ET.Element('description')
    description.text = u'News from %s' % LOCAL.variables['title']
    channel.append(description)
    link = ET.Element('link')
    link.text = host_url
    channel.append(link)

    for date, new in sorted(ordered_news.items(), reverse=True):
        id_string = new['datetime'] #new['title'].lower().replace(' ', '-').replace('.', '-')
        url = "%snews#%s" % (host_url, id_string)
        item = ET.Element('item')
        channel.append(item)
        title = ET.Element('title')
        #title.text = new['title']
        item.append(title)
        guid = ET.Element('guid')
        guid.text = str(hash(new))
        item.append(guid)
        date = ET.Element('pubDate')
        date.text = datetime.datetime.strptime(
            new['datetime'], '%Y-%m-%d@%H:%M:%S').strftime(
            '%a, %d %b %Y %H:%M:%S +0000')
        item.append(date)
        link = ET.Element('link')
        link.text = url
        item.append(link)

        parts = docutils.core.publish_parts(
            source=new['content'].read(),
            writer=docutils.writers.html4css1.Writer(),
            settings_overrides={'initial_header_level': 2})
        description_text = parts['fragment']
        description = ET.Element('description')
        description.text = description_text
        item.append(description)

    return ET.tostring(tree, 'utf-8')
