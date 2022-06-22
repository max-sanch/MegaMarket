import datetime
from uuid import UUID

from django.test import TestCase

from shop_unit.tests import config
from shop_unit import models


class ShopUnitTestCase(TestCase):
	def setUp(self):
		parent = models.ShopUnit.objects.create(
			uuid=config.UUID_OK,
			name="Test parent 1",
			date=datetime.datetime.fromisoformat("2022-02-01T00:00:00.000"),
			unit_type=models.ShopUnitType.CATEGORY
		)
		models.ShopUnit.objects.create(
			uuid=config.UUID_CHILDREN_1,
			name="Test children 1",
			date=datetime.datetime.fromisoformat("2022-02-01T00:00:00.000"),
			unit_type=models.ShopUnitType.OFFER,
			price=123,
			parent=parent
		)
		models.ShopUnit.objects.create(
			uuid=config.UUID_CHILDREN_2,
			name="Test children 2",
			date=datetime.datetime.fromisoformat("2022-02-01T00:00:00.000"),
			unit_type=models.ShopUnitType.OFFER,
			price=213,
			parent=parent
		)
		models.ShopUnit.objects.create(
			uuid=config.UUID_CHILDREN_3,
			name="Test children 3",
			date=datetime.datetime.fromisoformat("2022-02-01T00:00:00.000"),
			unit_type=models.ShopUnitType.OFFER,
			price=321,
			parent=parent
		)

	def test_get_ok(self):
		shop_unit = models.ShopUnit.objects.get(uuid=config.UUID_OK)
		self.assertEqual(shop_unit.uuid, UUID(config.UUID_OK))
		self.assertEqual(shop_unit.name, "Test parent 1")
		self.assertEqual(type(shop_unit.date), datetime.datetime)
		self.assertEqual(shop_unit.parent, None)
		self.assertEqual(shop_unit.price, None)

	def test_get_err(self):
		with self.assertRaises(models.ShopUnit.DoesNotExist):
			models.ShopUnit.objects.get(uuid=config.UUID_NOT_FOUND)

	def test_bfs_by_uuid_ok(self):
		shop_units_tree = models.ShopUnit.custom_objects.bfs_by_uuid(config.UUID_OK)
		self.assertEqual(len(shop_units_tree), 4)
		self.assertEqual(shop_units_tree[0].uuid, UUID(config.UUID_OK))
		self.assertEqual(shop_units_tree[1].parent_id, UUID(config.UUID_OK))
		self.assertEqual(shop_units_tree[2].parent_id, UUID(config.UUID_OK))
		self.assertEqual(shop_units_tree[3].parent_id, UUID(config.UUID_OK))

	def test_bfs_by_uuid_not_found(self):
		shop_units_tree = models.ShopUnit.custom_objects.bfs_by_uuid(config.UUID_NOT_FOUND)
		self.assertEqual(len(shop_units_tree), 0)

	def test_get_parent_price_ok(self):
		parent_price = models.ShopUnit.custom_objects.get_parent_price(config.UUID_OK)
		self.assertEqual(parent_price.ch_count, 3)
		self.assertEqual(parent_price.price, 657)

	def test_get_parent_price_not_found(self):
		parent_price = models.ShopUnit.custom_objects.get_parent_price(config.UUID_NOT_FOUND)
		self.assertEqual(parent_price.ch_count, 0)
		self.assertEqual(parent_price.price, None)


class ShopUnitStatisticTestCase(TestCase):
	def setUp(self):
		shop_unit = models.ShopUnit.objects.create(
			uuid=config.UUID_OK,
			name="Test shop_unit 1",
			date=datetime.datetime.fromisoformat("2022-02-01T00:00:00.000"),
			unit_type=models.ShopUnitType.CATEGORY
		)
		models.ShopUnitStatistic.objects.create(
			shop_unit=shop_unit,
			name="Test shop_unit_statistic 1",
			date=datetime.datetime.fromisoformat("2022-02-01T00:00:00.000"),
			unit_type=models.ShopUnitType.CATEGORY
		)

	def test_get_ok(self):
		shop_unit_stat = models.ShopUnitStatistic.objects.get(shop_unit__uuid=config.UUID_OK)
		self.assertEqual(shop_unit_stat.name, "Test shop_unit_statistic 1")
		self.assertEqual(type(shop_unit_stat.date), datetime.datetime)
		self.assertEqual(shop_unit_stat.parent_id, None)
		self.assertEqual(shop_unit_stat.price, None)

	def test_get_err(self):
		with self.assertRaises(models.ShopUnitStatistic.DoesNotExist):
			models.ShopUnitStatistic.objects.get(shop_unit__uuid=config.UUID_NOT_FOUND)
