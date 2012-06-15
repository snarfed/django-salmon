import base64
import urllib2
import datetime

from xml.etree import ElementTree
# dateutil.parser is imported lazily below, in verify_timestamp(), so that other
# modules in this package can be imported and used without requiring dateutil.


ATOM_NS = 'http://www.w3.org/2005/Atom'
MAGIC_ENV_NS = 'http://salmon-protocol.org/ns/magic-env'
XRD_NS = 'http://docs.oasis-open.org/ns/xri/xrd-1.0'

normalize = lambda tag, ns: "{%s}%s" % (ns, tag)


def create_magic_envelope(data, sig, mime_type='application/atom+xml',
                          encoding='base64url', alg='RSA-SHA256'):
    root = ElementTree.Element('me:env', attrib={'xmlns:me': MAGIC_ENV_NS})
    data_element = ElementTree.SubElement(root, 'me:data', attrib={
        'type': mime_type,
    })
    data_element.text = data
    encoding_element = ElementTree.SubElement(root, 'me:encoding')
    encoding_element.text = encoding
    alg_element = ElementTree.SubElement(root, 'me:alg')
    alg_element.text = alg
    me_sig = ElementTree.SubElement(root, 'me:sig')
    me_sig.text = sig
    return ElementTree.tostring(root)


def parse_magic_envelope(magic_envelope):
    et = ElementTree.fromstring(magic_envelope)
    data = [e for e in list(et) if e.tag == normalize('data', MAGIC_ENV_NS)]
    sig = [e for e in list(et) if e.tag == normalize('sig', MAGIC_ENV_NS)]
    return {
        'data': data[0].text,
        'sig': sig[0].text,
    }


def parse_author_uri_from_atom(data):
    et = ElementTree.fromstring(data)
    author_element = et.find(normalize('author', ATOM_NS))
    (name, uri) = author_element.getchildren()
    return uri.text


def parse_updated_from_atom(data):
    et = ElementTree.fromstring(data)
    if et.tag != normalize('entry', ATOM_NS):
        et = et.find(normalize('entry', ATOM_NS))
    updated = et.find(normalize('updated', ATOM_NS))
    return updated.text


def parse_host_xrd(xrd):
    et = ElementTree.fromstring(xrd)
    links = et.findall(normalize('Link', XRD_NS))
    lrdd_links = [link for link in links
                 if 'rel' in link.attrib and link.attrib['rel'] == 'lrdd']
    for link in lrdd_links:
        if 'template' in link.attrib:
            return link.attrib['template']
    return None


def parse_public_key_from_xrd(user_xrd):
    et = ElementTree.fromstring(user_xrd)
    links = et.findall(normalize('Link', XRD_NS))
    magic_sig_links = [link for link in links
                       if ('rel' in link.attrib
                           and link.attrib['rel'] == 'magic-public-key')]
    for link in magic_sig_links:
        if 'href' in link.attrib:
            return link.attrib['href'].split('.')[1:]  # TODO(paulosman)
    return None


def get_public_key(author_uri):
    if not author_uri.startswith('acct:'):
        return False  # not implemented yet
    (user, host) = author_uri[5:].split('@')
    url = 'http://%s/.well-known/host-meta' % (host,)
    f = urllib2.urlopen(url)
    host_xrd = f.read()
    uri_template = parse_host_xrd(host_xrd)
    webfinger_url = uri_template.replace('{uri}', author_uri[5:])
    f = urllib2.urlopen(webfinger_url)
    user_xrd = f.read()
    return parse_public_key_from_xrd(user_xrd)


def verify_timestamp(timestamp):
    from dateutil.parser import parse as parse_utc_date
    d = parse_utc_date(timestamp)
    d2 = datetime.datetime.now(d.tzinfo)
    delta = datetime.timedelta(hours=1)
    return d2 - d < delta


def decode(data):
    return base64.urlsafe_b64decode(data).encode('utf-8')


def encode(s):
    return base64.urlsafe_b64encode(
        unicode(s).encode('utf-8')).encode('utf-8')


def slap_handler(data, mime_type):
    pass


def slap_notify(data, mime_type):
    from django.conf import settings
    from django.utils.importlib import import_module

    notifier = getattr(settings, 'SALMON_SLAP_HANDLER',
                       'salmon.utils.slap_handler')
    notifier, notifier_function = notifier.rsplit('.', 1)
    notifier_module = import_module(notifier)
    return getattr(notifier_module, notifier_function)(data, mime_type)
