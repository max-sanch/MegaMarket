from uuid import UUID
from datetime import datetime

from shop_unit import models


def validate_uuid(uuid: str):
	try:
		UUID(uuid)
	except ValueError:
		raise ValueError("'id' does not match UUID format")

def validate_date(date: str):
	if type(date) is not str:
		raise ValueError("field 'updateDate' must be of type string")
	try:
		datetime.fromisoformat(date.replace('Z', ''))
	except ValueError:
		raise ValueError("field 'updateDate' does not conform to ISO 8601 format")

def validate_type(curr_type, new_type):
	if curr_type != new_type:
		raise ValueError("you may not edit an existing field 'unit_type'")

def validate_parent(parent: models.ShopUnit):
	if parent is not None and parent.unit_type == models.ShopUnitType.OFFER:
		raise ValueError("parent type cannot be OFFER")
