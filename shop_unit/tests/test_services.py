import json
import datetime
from uuid import UUID

from django.test import TestCase
from pydantic.error_wrappers import ValidationError

from shop_unit.tests.utils import deep_sort_children
from shop_unit import models, services
from shop_unit.tests import config


class ServicesImportsTestCase(TestCase):
	def setUp(self):
		self.data = services.ShopUnitImportRequest.parse_obj(config.IMPORT_BATCHES[1])
		self.unit_indexes = services._get_unit_indexes(self.data)

	def test_get_unit_indexes_ok(self):
		unit_indexes = services._get_unit_indexes(self.data)
		self.assertDictEqual(
			unit_indexes,
			{
				UUID(config.IMPORT_BATCHES[1]["items"][0]["id"]): 0,
				UUID(config.IMPORT_BATCHES[1]["items"][1]["id"]): 1,
				UUID(config.IMPORT_BATCHES[1]["items"][2]["id"]): 2,
			}
		)

	def test_get_unit_indexes_err(self):
		self.data.items.append(self.data.items[0])
		with self.assertRaisesMessage(ValueError, "there should not be multiple units with the same uuid"):
			services._get_unit_indexes(self.data)

	def test_get_parent_and_item_ok(self):
		self.data.items[0].parent_id = None

		parent, item = services._get_parent_and_item(0, self.data, self.unit_indexes)
		self.assertEqual(parent, None)
		self.assertEqual(item.uuid, UUID('d515e43f-f3f6-4471-bb77-6b455017a2d2'))

		models.ShopUnit.objects.create(
			uuid=item.uuid,
			name=item.name,
			date=self.data.update_date,
			parent=parent,
			unit_type=models.ShopUnitType[item.unit_type],
			price=item.price
		)

		parent, item = services._get_parent_and_item(1, self.data, self.unit_indexes)
		self.assertEqual(type(parent), models.ShopUnit)
		self.assertEqual(parent.uuid, UUID('d515e43f-f3f6-4471-bb77-6b455017a2d2'))
		self.assertEqual(item.uuid, UUID('863e1a7a-1304-42ae-943b-179184c077e3'))

	def test_get_parent_and_item_err(self):
		with self.assertRaisesMessage(ValueError, "parent with given uuid not found"):
			services._get_parent_and_item(0, self.data, self.unit_indexes)

	def test_add_unit_statistic_ok(self):
		shop_unit = models.ShopUnit.objects.create(
			uuid=config.UUID_OK,
			name="Test",
			date=datetime.datetime.now(),
			unit_type=models.ShopUnitType.CATEGORY
		)
		services._add_unit_statistic(shop_unit)
		unit_stats = models.ShopUnitStatistic.objects.get(shop_unit__uuid=config.UUID_OK)
		self.assertEqual(shop_unit.name, unit_stats.name)
		self.assertEqual(shop_unit.date, unit_stats.date)
		self.assertEqual(shop_unit.price, unit_stats.price)
		self.assertEqual(shop_unit.unit_type, unit_stats.unit_type)

	def test_create_or_update_units_ok(self):
		services.create_or_update_units(json.dumps(config.IMPORT_OK))

		shop_unit_parent = models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][1]["id"])
		self.assertEqual(shop_unit_parent.name, config.IMPORT_OK["items"][1]["name"])
		self.assertEqual(shop_unit_parent.parent_id, UUID(config.IMPORT_OK["items"][1]["parentId"]))
		self.assertEqual(shop_unit_parent.price, 69999)

		shop_unit = models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][0]["id"])
		self.assertEqual(shop_unit.name, config.IMPORT_OK["items"][0]["name"])
		self.assertEqual(shop_unit.parent, shop_unit_parent)

	def test_create_or_update_units_not_found(self):
		with self.assertRaisesMessage(ValueError, "parent with given uuid not found"):
			services.create_or_update_units(json.dumps(config.IMPORT_NOT_FOUND))

	def test_create_or_update_units_type_err_name(self):
		with self.assertRaises(ValidationError):
			services.create_or_update_units(json.dumps(config.IMPORT_TYPE_ERR_NAME))

	def test_create_or_update_units_type_err_price(self):
		with self.assertRaises(ValidationError):
			services.create_or_update_units(json.dumps(config.IMPORT_TYPE_ERR_PRICE))

	def test_create_or_update_units_format_err_date(self):
		with self.assertRaises(ValidationError):
			services.create_or_update_units(json.dumps(config.IMPORT_FORMAT_ERR_DATE))


class ServicesDeleteTestCase(TestCase):
	def setUp(self):
		services.create_or_update_units(json.dumps(config.IMPORT_OK))

	def test_delete_shop_unit_ok(self):
		shop_unit = models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][1]["id"])
		self.assertEqual(shop_unit.name, config.IMPORT_OK["items"][1]["name"])

		shop_unit = models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][0]["id"])
		self.assertEqual(shop_unit.name, config.IMPORT_OK["items"][0]["name"])

		services.delete_shop_unit(config.IMPORT_OK["items"][1]["id"])
		with self.assertRaises(models.ShopUnit.DoesNotExist):
			models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][1]["id"])

		with self.assertRaises(models.ShopUnit.DoesNotExist):
			models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][0]["id"])

	def test_delete_shop_unit_update_price(self):
		shop_unit = models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][1]["id"])
		self.assertEqual(shop_unit.name, config.IMPORT_OK["items"][1]["name"])
		self.assertEqual(shop_unit.price, 69999)

		services.delete_shop_unit(config.IMPORT_OK["items"][0]["id"])
		with self.assertRaises(models.ShopUnit.DoesNotExist):
			models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][0]["id"])

		shop_unit = models.ShopUnit.objects.get(uuid=config.IMPORT_OK["items"][1]["id"])
		self.assertEqual(shop_unit.name, config.IMPORT_OK["items"][1]["name"])
		self.assertEqual(shop_unit.price, 59999)

	def test_delete_shop_unit_not_found(self):
		with self.assertRaises(models.ShopUnit.DoesNotExist):
			services.delete_shop_unit(config.UUID_NOT_FOUND)

	def test_delete_shop_unit_err(self):
		with self.assertRaisesMessage(ValueError, "uuid does not match UUID format"):
			services.delete_shop_unit("err_uuid")


class ServicesNodesTestCase(TestCase):
	def setUp(self):
		services.create_or_update_units(json.dumps(config.IMPORT_OK))

	def test_get_shop_unit_by_uuid_ok(self):
		shop_unit_tree = services.get_shop_unit_by_uuid(config.UUID_OK)
		self.assertEqual(deep_sort_children(shop_unit_tree), deep_sort_children(config.NODE_TREE_OK))

	def test_get_shop_unit_by_uuid_not_found(self):
		shop_unit_tree = services.get_shop_unit_by_uuid(config.UUID_NOT_FOUND)
		self.assertTrue(not shop_unit_tree)

	def test_delete_shop_unit_err(self):
		with self.assertRaisesMessage(ValueError, "uuid does not match UUID format"):
			services.get_shop_unit_by_uuid("err_uuid")


class ServicesSalesTestCase(TestCase):
	def setUp(self):
		services.create_or_update_units(json.dumps(config.IMPORT_OK))

	def test_get_sales_ok(self):
		units = services.get_sales("2022-02-01T12:00:00.000Z")
		self.assertEqual(len(units["items"]), 2)
		units = services.get_sales("2022-02-02T12:00:00.000Z")
		self.assertEqual(len(units["items"]), 2)

	def test_get_sales_not_found(self):
		units = services.get_sales("2022-02-02T12:00:01.000Z")
		self.assertEqual(len(units["items"]), 0)
		units = services.get_sales("2022-01-31T23:59:59.999Z")
		self.assertEqual(len(units["items"]), 0)

	def test_get_sales_format_err_date(self):
		with self.assertRaisesMessage(ValueError, "date does not conform to ISO 8601 format"):
			services.get_sales("2022.02.02 12:00:01")


class ServicesNodeStatisticTestCase(TestCase):
	def setUp(self):
		services.create_or_update_units(json.dumps(config.IMPORT_OK))

	def test_get_node_statistic_ok(self):
		units = services.get_node_statistic(
			config.UUID_OK,
			"2022-02-01T12:00:00.000Z",
			"2022-02-01T12:00:01.000Z",
		)
		self.assertEqual(len(units["items"]), 1)

		services.create_or_update_units(json.dumps(config.IMPORT_UPDATE_OK))

		units = services.get_node_statistic(
			config.UUID_OK,
			"2022-02-01T12:00:00.000Z",
			"2022-02-01T12:00:01.000Z",
		)
		self.assertEqual(len(units["items"]), 1)

		units = services.get_node_statistic(
			config.UUID_OK,
			"2022-02-01T12:00:00.000Z",
			"2022-02-01T12:00:02.000Z",
		)
		self.assertEqual(len(units["items"]), 2)

	def test_get_node_statistic_not_found(self):
		with self.assertRaises(models.ShopUnitStatistic.DoesNotExist):
			services.get_node_statistic(
				config.UUID_NOT_FOUND,
				"2022-02-01T12:00:00.000Z",
				"2022-02-02T12:00:00.000Z",
			)

	def test_get_node_statistic_format_err_date(self):
		with self.assertRaisesMessage(ValueError, "date does not conform to ISO 8601 format"):
			services.get_node_statistic(
				config.UUID_OK,
				"2022-02-01T12:00:00.000Z",
				"2022.02.02 12:00:00",
			)

	def test_get_node_statistic_type_err_uuid(self):
		with self.assertRaisesMessage(ValueError, "uuid does not match UUID format"):
			services.get_node_statistic(
				"err uuid",
				"2022-02-01T12:00:00.000Z",
				"2022-02-02T12:00:00.000Z",
			)
