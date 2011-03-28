from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from salmon import utils


@csrf_exempt
@require_POST
def endpoint(request):
    parsed = utils.parse_magic_envelope(request.raw_post_data)
    parsed['data'] = utils.decode(parsed['data'])

    # TODO(paulosman) - verify sender

    # hand waving on mime_type right now, but seems like this'd be
    # a decent interface.
    utils.slap_notify(parsed['data'], 'application/atom+xml')

    return HttpResponse('slapped: %s' % (parsed,))
