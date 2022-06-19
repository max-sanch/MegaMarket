from datetime import datetime
from uuid import UUID

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
	update_date: str = Field(alias="updateDate")

	@validator('update_date')
	def update_date_format(cls, v):
		try:
			datetime.fromisoformat(v.replace('Z', ''))
		except ValueError:
			raise ValueError("field 'updateDate' does not conform to ISO 8601 format")
		return v


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
			"date": unit.date,
			"parentId": unit.parent.uuid if unit.parent is not None else None,
			"type": models.ShopUnitType[unit.unit_type],
			"price": unit.price
		}

		if curr_unit["type"] == models.ShopUnitType.CATEGORY:
			curr_unit["children"] = []
			parent_links[curr_unit["id"]] = curr_unit["children"]

		if not head_unit:
			head_unit = curr_unit
		else:
			parent_links[curr_unit["parentId"]].append(curr_unit)
	return head_unit


def update_parent_price(units, date=None):
	for unit in units:
		curr_unit = unit
		while curr_unit is not None:
			sum_price = models.ShopUnit.custom_objects.get_parent_price(str(curr_unit.uuid))
			if sum_price.price is None:
				curr_unit.price = None
			else:
				curr_unit.price = sum_price.price // sum_price.ch_count
			if date is not None:
				curr_unit.date = date
			curr_unit.save()
			curr_unit = curr_unit.parent
