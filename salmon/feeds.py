from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed, get_tag_uri
from django.utils.xmlutils import SimplerXMLGenerator

ATOM_NS = 'http://www.w3.org/2005/Atom'
ATOM_THREADING_NS = 'http://purl.org/syndication/thread/1.0'


class SalmonAtom1Feed(Atom1Feed):

    def add_root_elements(self, handler):
        salmon = self.feed.get('salmon-endpoint')
        if salmon is not None:
            handler.addQuickElement(u'link', '', {u'rel': u'salmon',
                                                  u'href': salmon})
        super(SalmonAtom1Feed, self).add_root_elements(handler)

    def add_item_elements(self, handler, item):
        if 'parent_href' in item and 'parent_updated' in item:
            handler.addQuickElement('thr:in-reply-to',
                                    get_tag_uri(item['parent_href'],
                                                item['parent_updated']))
        super(SalmonAtom1Feed, self).add_item_elements(handler, item)

    def root_attributes(self):
        """Put the Atom namespace into the root element."""
        return {
            'xmlns': ATOM_NS,
            'xmlns:thr': ATOM_THREADING_NS,
        }


class SalmonAtom1EntryFeed(Atom1Feed):
    def item_attributes(self):
        """Put the Atom namespace into the root element."""
        return {
            'xmlns': ATOM_NS,
            'xmlns:thr': ATOM_THREADING_NS,
        }


class SalmonFeed(Feed):
    feed_type = SalmonAtom1Feed

    def get_object(self, request):
        super(SalmonFeed, self).get_object(request)
        self._request = request

    def feed_extra_kwargs(self, obj):
        endpoint = self._request.build_absolute_uri(reverse('salmon_endpoint'))
        return {
            'salmon-endpoint': endpoint,
        }


def create_entry_feed(title, link, description, author_name,
                      author_link, pubdate, parent_href, parent_updated):
    feed = SalmonAtom1EntryFeed(title='', link='', description='')
    feed.add_item(
        title, link, description,
        author_name=author_name, author_link=author_link, pubdate=pubdate,
        parent_href=parent_href, parent_updated=parent_updated,
    )
    sb = StringIO()
    sb.write(u'<?xml version="1.0" encoding="utf-8"?>')
    handler = SimplerXMLGenerator(out=sb)
    feed.write_items(handler)
    return sb.getvalue()
