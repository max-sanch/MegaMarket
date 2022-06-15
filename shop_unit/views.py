import json

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse


@require_http_methods(["POST"])
def imports(request):
	data = json.loads(request.read())
	return JsonResponse(data)


@require_http_methods(["DELETE"])
def delete(request, uuid):
	return JsonResponse({'data': uuid})


@require_http_methods(["GET"])
def nodes(request, uuid):
	return JsonResponse({'data': uuid})
