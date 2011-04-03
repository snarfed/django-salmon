from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from salmon import utils, magicsigs


@csrf_exempt
@require_POST
def endpoint(request):
    parsed = utils.parse_magic_envelope(request.raw_post_data)
    parsed['data'] = utils.decode(parsed['data'])

    # verify that data was signed by sender
    author_uri = utils.parse_author_uri_from_atom(parsed['data'])
    if not magicsigs.verify(author_uri, parsed['data'], parsed['sig']):
        return HttpResponseBadRequest("Could not verify magic signature.")

    # hand waving on mime_type right now, but seems like this'd be
    # a decent interface.
    utils.slap_notify(parsed['data'], 'application/atom+xml')

    return HttpResponse('slapped: %s' % (parsed,))
