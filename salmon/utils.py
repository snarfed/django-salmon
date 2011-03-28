import base64
from xml.etree import ElementTree

from django.conf import settings
from django.utils.importlib import import_module

MAGIC_ENV_NS = 'http://salmon-protocol.org/ns/magic-env'


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
    normalize = lambda tag: "{%s}%s" % (MAGIC_ENV_NS, tag)
    data = [e for e in list(et) if e.tag == normalize('data')]
    sig = [e for e in list(et) if e.tag == normalize('sig')]
    return {
        'data': data[0].text,
        'sig': sig[0].text,
    }


def decode(data):
    return base64.urlsafe_b64decode(data).encode('utf-8')


def encode(s):
    return base64.urlsafe_b64encode(
        unicode(s).encode('utf-8')).encode('utf-8')


def slap_handler(data, mime_type):
    pass


def slap_notify(data, mime_type):
    notifier = getattr(settings, 'SALMON_SLAP_HANDLER',
                       'salmon.utils.slap_handler')
    notifier, notifier_function = notifier.rsplit('.', 1)
    notifier_module = import_module(notifier)
    return getattr(notifier_module, notifier_function)(data, mime_type)
