import datetime
from uuid import UUID

from django.conf import settings
from django.db import transaction
from pydantic import BaseModel, Field, validator, root_validator

from shop_unit import models, validations


class ImportUnit(BaseModel):
	uuid: UUID = Field(alias="id")
	parent_id: UUID = Field(alias="parentId", default=None)
	unit_type: models.ShopUnitType = Field(alias="type")
	price: int = None
	name: str

	@validator('price', pre=True, allow_reuse=True)
	def price_type_and_value(cls, v):
		if v is not None:
			if type(v) is not int:
				raise ValueError("field 'price' must be of type integer")
			if v < 0:
				raise ValueError("price must be greater than or equal to zero")
		return v

	@validator('name', pre=True, allow_reuse=True)
	def name_type(cls, v):
		if type(v) is not str:
			raise ValueError("field 'name' must be of type string")
		return v

	@root_validator(allow_reuse=True)
	def offer_and_category_price(cls, values):
		if values.get("unit_type") == models.ShopUnitType.CATEGORY and values.get("price") is not None:
			raise ValueError("field 'price' must be empty for CATEGORY")
		if values.get("unit_type") == models.ShopUnitType.OFFER and values.get("price") is None:
			raise ValueError("field 'price' cannot be empty for OFFER")
		return values


class ImportData(BaseModel):
	items: list[ImportUnit]
	update_date: datetime.datetime = Field(alias="updateDate")

	@validator('update_date', pre=True)
	def update_date_format(cls, v):
		try:
			datetime.datetime.fromisoformat(v.replace('Z', ''))
		except ValueError:
			raise ValueError("field 'updateDate' does not conform to ISO 8601 format")
		return v.replace('Z', '+00:00')


@transaction.atomic
def create_or_update_units(data):
	import_data = ImportData.parse_raw(data)
	unit_indexes = {}
	unit_set = set()

	for i in range(len(import_data.items)):
		item = import_data.items[i]

		if unit_indexes.get(item.uuid) is None:
			unit_indexes[item.uuid] = i
		else:
			raise ValueError("there should not be multiple units with the same uuid")

	for i in range(len(import_data.items)):
		item = import_data.items[i]
		parent = None

		while item.parent_id is not None:
			try:
				parent = models.ShopUnit.objects.get(uuid=item.parent_id)
				break
			except models.ShopUnit.DoesNotExist:
				if unit_indexes.get(item.parent_id) is None:
					raise ValueError("parent with given uuid not found")
				else:
					parent_idx = unit_indexes[item.parent_id]
					import_data.items[i], import_data.items[parent_idx] \
						= import_data.items[parent_idx], import_data.items[i]
					unit_indexes[item.uuid], unit_indexes[item.parent_id] = \
						unit_indexes[item.parent_id], unit_indexes[item.uuid]
					item = import_data.items[i]

		unit, created = models.ShopUnit.objects.get_or_create(
			uuid=item.uuid,
			defaults={
				"name": item.name,
				"date": import_data.update_date,
				"parent": parent,
				"unit_type": models.ShopUnitType[item.unit_type],
				"price": item.price
			}
		)

		if not created:
			validations.validate_type(unit.unit_type, models.ShopUnitType[item.unit_type])
			unit.name = item.name
			unit.date = import_data.update_date
			unit.parent = parent
			unit.unit_type = models.ShopUnitType[item.unit_type]
			unit.price = item.price

		validations.validate_parent(unit.parent)

		if unit.unit_type == models.ShopUnitType.CATEGORY:
			curr_unit = unit
		else:
			add_unit_statistic(unit)
			curr_unit = unit.parent

		if curr_unit is not None:
			unit_set.add(curr_unit)
			if curr_unit.parent is not None and curr_unit.parent in unit_set:
				unit_set.remove(curr_unit.parent)
		unit.save()
	update_parent_price(unit_set, import_data.update_date)


def delete_shop_unit(uuid):
	validations.validate_uuid(uuid)
	unit = models.ShopUnit.objects.get(uuid=uuid)
	parent = unit.parent
	unit.delete()
	update_parent_price((parent,))


def get_shop_unit_by_uuid(uuid: str) -> dict:
	validations.validate_uuid(uuid)
	units = models.ShopUnit.custom_objects.bfs_by_uuid(uuid=uuid)
	parent_links = {}
	head_unit = {}

	for unit in units:
		curr_unit = {
			"id": unit.uuid,
			"name": unit.name,
			"date": unit.date.strftime(settings.DATETIME_FORMAT)[:-3] + "Z",
			"parentId": unit.parent.uuid if unit.parent is not None else None,
			"type": models.ShopUnitType[unit.unit_type],
			"price": unit.price
		}

		if curr_unit["type"] == models.ShopUnitType.CATEGORY:
			curr_unit["children"] = []
			parent_links[curr_unit["id"]] = curr_unit["children"]
		else:
			curr_unit["children"] = None

		if not head_unit:
			head_unit = curr_unit
		else:
			parent_links[curr_unit["parentId"]].append(curr_unit)
	return head_unit


def get_sales(date_str: str) -> dict:
	try:
		date = datetime.datetime.fromisoformat(date_str.replace('Z', ''))
	except ValueError:
		raise ValueError("date does not conform to ISO 8601 format")

	start = date - datetime.timedelta(days=1)
	print(start, date)
	response_data = {"items": []}

	for unit in models.ShopUnit.objects.filter(date__gte=start, date__lte=date, unit_type=models.ShopUnitType.OFFER):
		response_data["items"].append({
			"id": unit.uuid,
			"name": unit.name,
			"date": unit.date.strftime(settings.DATETIME_FORMAT)[:-3] + "Z",
			"parentId": unit.parent.uuid if unit.parent is not None else None,
			"price": unit.price,
			"type": unit.unit_type
		})
	return response_data


def get_node_statistic(uuid: str, date_start_str: str, date_end_str: str) -> dict:
	validations.validate_uuid(uuid)
	try:
		date_start = datetime.datetime.fromisoformat(date_start_str.replace('Z', ''))
		date_end = datetime.datetime.fromisoformat(date_end_str.replace('Z', ''))
	except ValueError:
		raise ValueError("date does not conform to ISO 8601 format")

	response_data = {"items": []}
	unit_statistic = models.ShopUnitStatistic.objects.filter(
		date__gte=date_start,
		date__lt=date_end,
		shop_unit__uuid=uuid
	)

	if len(unit_statistic) == 0:
		raise models.ShopUnitStatistic.DoesNotExist("units with given parameters were not found")

	for unit in unit_statistic:
		response_data["items"].append({
			"id": unit.shop_unit.uuid,
			"name": unit.name,
			"date": unit.date.strftime(settings.DATETIME_FORMAT)[:-3] + "Z",
			"parentId": unit.parent_id,
			"price": unit.price,
			"type": unit.unit_type
		})
	return response_data


def update_parent_price(units: list[models.ShopUnit], date=None):
	for curr_unit in units:
		while curr_unit is not None:
			parent_price = models.ShopUnit.custom_objects.get_parent_price(str(curr_unit.uuid))

			if parent_price.price is None:
				curr_unit.price = None
			else:
				curr_unit.price = parent_price.price // parent_price.ch_count

			if date is not None:
				curr_unit.date = date
			curr_unit.save()
			add_unit_statistic(curr_unit)
			curr_unit = curr_unit.parent


def add_unit_statistic(unit: models.ShopUnit):
	unit_statistic = models.ShopUnitStatistic(
		shop_unit=unit,
		name=unit.name,
		date=unit.date,
		parent_id=unit.parent.uuid if unit.parent is not None else None,
		unit_type=unit.unit_type,
		price=unit.price
	)
	unit_statistic.save()
