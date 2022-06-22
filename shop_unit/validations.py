from uuid import UUID
from shop_unit import models


def validate_uuid(uuid: str) -> None:
	"""Проверяет корректность UUID"""

	try:
		UUID(uuid)
	except ValueError:
		raise ValueError("uuid does not match UUID format")

def validate_type(curr_type: models.ShopUnitType, new_type: models.ShopUnitType) -> None:
	"""Проверяет неизменность типа"""

	if curr_type != new_type:
		raise ValueError("you may not edit an existing field 'unit_type'")

def validate_parent(parent: models.ShopUnit) -> None:
	"""Проверяет является ли родитель категорией"""

	if parent is not None and parent.unit_type == models.ShopUnitType.OFFER:
		raise ValueError("parent type cannot be OFFER")
