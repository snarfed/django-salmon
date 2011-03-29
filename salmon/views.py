from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from salmon import utils


@csrf_exempt
@require_POST
def endpoint(request):
    parsed = utils.parse_magic_envelope(request.raw_post_data)
    parsed['data'] = utils.decode(parsed['data'])

    # verify that data was signed by sender
    author_uri = utils.parse_author_uri_from_atom(parsed['data'])
    if not utils.verify_signature(author_uri, parsed['data'], parsed['sig']):
        return HttpResponseForbidden()

    # hand waving on mime_type right now, but seems like this'd be
    # a decent interface.
    utils.slap_notify(parsed['data'], 'application/atom+xml')

    return HttpResponse('slapped: %s' % (parsed,))
