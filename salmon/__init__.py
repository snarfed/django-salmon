import urllib2
import feedparser

from salmon import magicsigs
from salmon.models import Subscription, UserKeyPair


def discover_salmon_endpoint(url):
    """
    Perform discovery on ``url``. Look for link[rel='salmon'] and
    fetch the href.
    """
    d = feedparser.parse(url)
    weblinks = getattr(d.feed, 'links', [])
    for link in weblinks:
        link_dict = dict(link)
        if 'rel' in link_dict and link_dict['rel'] == 'salmon':
            if 'href' in link:
                return link['href']
    return None


def subscribe(feed, feed_url):
    """
    Perform discovery on feed to find salmon endpoint URI.

    ``feed`` is the feed object, however it is represented in your system.
    ``feed_url`` is the URL of the Atom / RSS feed.
    """
    salmon_endpoint = discover_salmon_endpoint(feed_url)
    if not salmon_endpoint:
        return None
    return Subscription.objects.subscribe(feed, salmon_endpoint)


def unsubscribe(feed):
    """Destroy a subscription to the feed object ``feed``."""
    Subscription.objects.unsubscribe(feed)


def slap(content, source, user):
    """Notify a source of updated content."""
    sub = Subscription.objects.get_for_object(source)
    if not sub:
        return  # nothing to do

    keypair = UserKeyPair.objects.get_or_create(user)

    # hand waving on mime_type right now
    magic_envelope = magicsigs.magic_envelope(
        content, 'application/atom+xml', keypair)

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
