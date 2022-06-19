from django.db import models


class ShopUnitType(models.TextChoices):
	OFFER = "OFFER"
	CATEGORY = "CATEGORY"


class CustomManager(models.Manager):
	def bfs_by_uuid(self, uuid: str):
		return super().raw("""
			WITH RECURSIVE tree(uuid, name, date, parent_id, unit_type, price, lvl) AS (
				SELECT uuid, name, date, parent_id, unit_type, price, 0
				FROM shop_unit_shopunit WHERE uuid = %s
			  UNION ALL
				SELECT su.uuid, su.name, su.date, su.parent_id, su.unit_type, su.price, lvl + 1
				FROM shop_unit_shopunit AS su INNER JOIN tree AS t on su.parent_id = t.uuid
			) SELECT * FROM tree order by lvl;
		""", params=(uuid.replace("-", ""),))

	def get_parent_price(self, uuid: str):
		return super().raw(
			"SELECT uuid, SUM(price) AS price, count(uuid) AS ch_count FROM shop_unit_shopunit WHERE parent_id = %s",
			params=(uuid.replace("-", ""),)
		)[0]


class ShopUnit(models.Model):
	uuid = models.UUIDField(
		primary_key=True,
		verbose_name="Уникальный идентификатор",
	)
	name = models.CharField(
		max_length=2048,
		verbose_name="Имя товара/категории",
	)
	date = models.CharField(
		max_length=32,
		verbose_name="Время последнего обновления элемента",
	)
	parent = models.ForeignKey(
		'self',
		null=True,
		default=None,
		on_delete=models.CASCADE
	)
	unit_type = models.CharField(
		max_length=8,
		choices=ShopUnitType.choices,
		verbose_name="Тип элемента - категория или товар",
	)
	price = models.PositiveBigIntegerField(
		null=True,
		default=None,
		verbose_name="Целое число, для категории - это средняя цена всех дочерних товаров",
	)
	objects = models.Manager()
	custom_objects = CustomManager()


class ShopUnitStatistic(models.Model):
	shop_unit = models.ForeignKey(
		'ShopUnit',
		on_delete=models.CASCADE,
	)
	name = models.CharField(
		max_length=2048,
		verbose_name="Имя товара/категории",
	)
	date = models.CharField(
		max_length=32,
		verbose_name="Время последнего обновления элемента",
	)
	parentId = models.UUIDField(
		null=True,
		default=None,
		db_index=True,
		verbose_name="UUID родительской категории",
	)
	unit_type = models.CharField(
		max_length=8,
		choices=ShopUnitType.choices,
		verbose_name="Тип элемента - категория или товар",
	)
	price = models.PositiveBigIntegerField(
		null=True,
		default=None,
		verbose_name="Целое число, для категории - это средняя цена всех дочерних товаров",
	)
