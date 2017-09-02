import base64
import logging
import re

from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util import number

from django_salmon import utils

_WHITESPACE_RE = re.compile(r'\s+')
_KEY_RE = re.compile(
    r"""RSA\.
    (?P<mod>[^\.]+)
    \.
    (?P<exp>[^\.]+)
    (?:\.
    (?P<private_exp>[^\.]+)
    )?""",
    re.VERBOSE)


def base64_to_long(x):
    """Convert ``x`` from URL safe base64 encoding to a long integer."""
    return number.bytes_to_long(base64.urlsafe_b64decode(x))


def long_to_base64(x):
    """Convert ``x`` from a long integer to base64 URL safe encoding."""
    return base64.urlsafe_b64encode(number.long_to_bytes(x))


def extract_key_details(key):
    """
    Given a URL safe base64 encoded RSA key pair, return the modulus,
    public exponent and private exponent as a tuple of long integers.
    This is the format expected by ``Crypto.PublicKey.RSA.construct``.
    """
    match = _KEY_RE.match(key)
    b64_to_num = lambda a: number.bytes_to_long(base64.urlsafe_b64decode(a))
    return (
        b64_to_num(match.group('mod')),
        b64_to_num(match.group('exp')),
        b64_to_num(match.group('private_exp')),
    )


def generate(bits=1024):
    """
    Generate an RSA keypair and return the modulus, public exponent and private
    exponent as a URL safe base64 encoded strings.
    """
    rng = Random.new().read
    key = RSA.generate(bits, rng)
    # e - public exponent, n - modulus, d - private exponent
    return (long_to_base64(key.e),
            long_to_base64(key.n),
            long_to_base64(key.d))


def sign(encoded_data, keypair):
    """
    Sign the data.
    """
    hash = SHA256.new(encoded_data)
    sig_bytes = pkcs1_15.new(keypair).sign(hash)
    return base64.urlsafe_b64encode(sig_bytes)


def verify(data, signed, author_uri=None, key=None):
    """Verify that ``signed`` is ``data`` signed by ``author_uri`` or ``key``."""
    assert (author_uri is None) != (key is None)
    if key:
      public_exp = key.public_exponent
      mod = key.mod
    else:
      mod, public_exp = utils.get_public_key(author_uri)

    keypair = RSA.construct((base64_to_long(mod), base64_to_long(public_exp)))
    hash = SHA256.new(sig_plaintext(data))
    try:
      pkcs1_15.new(keypair).verify(hash, base64.urlsafe_b64decode(signed))
      return True
    except (ValueError, TypeError) as e:
      logging.info(e)
      return False


def magic_envelope(raw_data, data_type, key):
    """Wrap the provided data in a magic envelope."""
    logging.debug('Signing key: %s %s', key.public_exponent, key.mod)
    rsa = RSA.construct(
        (base64_to_long(key.mod),
         base64_to_long(key.public_exponent),
         base64_to_long(key.private_exponent)))
    signed = sign(sig_plaintext(raw_data), rsa)
    return utils.create_magic_envelope(raw_data, signed.decode())


def sig_plaintext(raw_data):
    text = b'.'.join(base64.urlsafe_b64encode(x) for x in
        (raw_data.encode('utf-8'), b'application/atom+xml', b'base64url', b'RSA-SHA256'))
    logging.info('Signing plaintext %s', text)
    return text
