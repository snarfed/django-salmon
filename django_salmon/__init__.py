import urllib2

from django_salmon import magicsigs
# feedparser and models.py are imported lazily in the methods below so that
# other modules in this package can be imported and used without requiring
# feedparser or Django.

SALMON_LINK_RELS = (
    'salmon',
    'salmon-reply',
    'http://salmon-protocol.org/ns/salmon-replies',
    )


def discover_salmon_endpoint(url_or_string):
    """
    Perform discovery on ``url_or_string``. Look for link[rel='salmon'] and
    fetch the href.
    """
    import feedparser

    def get_salmon_replies_link(e):
        """Helper function. fetch href of link[rel=salmon] if it exists."""
        weblinks = getattr(e, 'links', [])
        for link in weblinks:
            link_dict = dict(link)
            if link_dict.get('rel') in SALMON_LINK_RELS:
                if 'href' in link_dict:
                    return link_dict['href']
        return None

    d = feedparser.parse(url_or_string)
    if len(d.entries) == 1:
        # parse out salmon for single atom:entry
        element = d.entries[0]
    else:
        element = d.feed
    return get_salmon_replies_link(element)


def subscribe(feed, feed_url):
    """
    Perform discovery on feed to find salmon endpoint URI.

    ``feed`` is the feed object, however it is represented in your system.
    ``feed_url`` is the URL of the Atom / RSS feed.
    """
    from django_salmon.models import Subscription

    salmon_endpoint = discover_salmon_endpoint(feed_url)
    if not salmon_endpoint:
        return None
    return Subscription.objects.subscribe(feed, salmon_endpoint)


def unsubscribe(feed):
    """Destroy a subscription to the feed object ``feed``."""
    from django_salmon.models import Subscription
    Subscription.objects.unsubscribe(feed)


def slap(content, source, user, mime_type='application/atom+xml'):
    """Notify a source of updated content."""
    from django_salmon.models import Subscription, UserKeyPair

    sub = Subscription.objects.get_for_object(source)
    if not sub:
        return  # nothing to do

    keypair = UserKeyPair.objects.get_or_create(user)
    magic_envelope = magicsigs.magic_envelope(
        content, mime_type, keypair)

    # TODO(paulosman)
    # really crappy HTTP client right now. Can improve when the basic
    # protocol flow is working.
    headers = {
        'Content-Type': 'application/magic-envelope+xml',
    }
    req = urllib2.Request(sub.salmon_endpoint, magic_envelope, headers)
    try:
        response = urllib2.urlopen(req)
        print response.read()
    except urllib2.HTTPError, e:
        print repr(e)
        print e.read()
