from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse

from shop_unit import services, models


class ErrorResponse(JsonResponse):
	def __init__(self, code: int, message: str, **kwargs):
		self.code = code
		self.message = message
		super().__init__(self.get_data(), status=code, **kwargs)

	def get_data(self):
		return {"code": self.code, "message": self.message}

@require_http_methods(["POST"])
def imports(request):
	services.create_or_update_units(request.read())
	return HttpResponse(content_type="application/json")

	# try:
	# 	services.create_or_update_units(request.read())
	# except Exception:
	# 	return ErrorResponse(400, "Validation Failed")
	# return HttpResponse(content_type="application/json")

@require_http_methods(["DELETE"])
def delete(request, uuid):
	try:
		services.delete_shop_unit(uuid)
	except models.ShopUnit.DoesNotExist:
		return ErrorResponse(404, "Item not found")
	except Exception:
		return ErrorResponse(400, "Validation Failed")
	return HttpResponse(content_type="application/json")

@require_http_methods(["GET"])
def nodes(request, uuid):
	try:
		unit = services.get_shop_unit_by_uuid(uuid)
		if not unit:
			return ErrorResponse(404, "Item not found")
	except Exception:
		return ErrorResponse(400, "Validation Failed")
	return JsonResponse(unit)
