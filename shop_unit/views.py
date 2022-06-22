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
	try:
		services.create_or_update_units(request.read())
	except Exception:
		return ErrorResponse(400, "Validation Failed")
	return HttpResponse(content_type="application/json")


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


@require_http_methods(["GET"])
def sales(request):
	try:
		date = request.headers.get("date") if request.GET.get('date') is None else request.GET.get('date')
		units = services.get_sales(date)
	except Exception:
		return ErrorResponse(400, "Validation Failed")
	return JsonResponse(units)


@require_http_methods(["GET"])
def node_statistic(request, uuid):
	try:
		date_start = request.headers.get("dateStart") if request.GET.get('dateStart') is None else request.GET.get(
			'dateStart')
		date_end = request.headers.get("dateEnd") if request.GET.get('dateEnd') is None else request.GET.get('dateEnd')
		units = services.get_node_statistic(uuid, date_start, date_end)
	except models.ShopUnitStatistic.DoesNotExist:
		return ErrorResponse(404, "Item not found")
	except Exception:
		return ErrorResponse(400, "Validation Failed")
	return JsonResponse(units)
