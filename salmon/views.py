from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from salmon import utils


@csrf_exempt
@require_POST
def endpoint(request):
    parsed = utils.parse_magic_envelope(request.raw_post_data)
    parsed['data'] = utils.decode(parsed['data'])
    return HttpResponse('slapped: %s' % (parsed,))
