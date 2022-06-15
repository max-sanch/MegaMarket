from django.db import models


SHOP_UNIT_TYPE = (
	(1, "OFFER"),
	(2, "CATEGORY")
)

class ShopUnit(models.Model):
	uuid = models.UUIDField(
		primary_key=True,
		verbose_name="Уникальный идентификатор",
	)
	name = models.CharField(
		max_length=2048,
		verbose_name="Имя товара/категории",
	)
	date = models.DateTimeField(
		verbose_name="Время последнего обновления элемента",
	)
	parent = models.ForeignKey(
		'self',
		on_delete=models.CASCADE,
	)
	type = models.IntegerField(
		choices=SHOP_UNIT_TYPE,
		verbose_name="Тип элемента - категория или товар",
	)
	price = models.BigIntegerField(
		null=True,
		default=None,
		verbose_name="Целое число, для категории - это средняя цена всех дочерних товаров",
	)


class ShopUnitStatistic(models.Model):
	shop_unit = models.ForeignKey(
		'ShopUnit',
		on_delete=models.CASCADE,
	)
	name = models.CharField(
		max_length=2048,
		verbose_name="Имя товара/категории",
	)
	date = models.DateTimeField(
		verbose_name="Время последнего обновления элемента",
	)
	parentId = models.UUIDField(
		null=True,
		default=None,
		db_index=True,
		verbose_name="UUID родительской категории",
	)
	type = models.IntegerField(
		choices=SHOP_UNIT_TYPE,
		verbose_name="Тип элемента - категория или товар",
	)
	price = models.BigIntegerField(
		null=True,
		default=None,
		verbose_name="Целое число, для категории - это средняя цена всех дочерних товаров",
	)
