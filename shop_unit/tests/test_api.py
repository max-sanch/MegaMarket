import json
import datetime
import urllib.parse

from django.test import TestCase, Client
from django.urls import reverse

from shop_unit.tests.utils import deep_sort_children
from shop_unit.tests import config
from shop_unit import models


class ImportsTestCase(TestCase):
	def setUp(self):
		self.client = Client()

	def test_imports_ok(self):
		for batch in config.IMPORT_BATCHES:
			response = self.client.post(reverse('imports'), data=batch, content_type="application/json")
			self.assertEqual(response.status_code, 200)

	def test_imports_err(self):
		response = self.client.post(reverse('imports'), data=config.IMPORT_BATCHES[1], content_type="application/json")
		self.assertEqual(response.status_code, 400)


class DeleteTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		models.ShopUnit.objects.create(
			uuid=config.UUID_OK,
			name="Test",
			date=datetime.datetime.now(),
			unit_type=models.ShopUnitType.CATEGORY
		)

	def test_delete_ok(self):
		response = self.client.delete(reverse('delete', args=(config.UUID_OK,)))
		self.assertEqual(response.status_code, 200)

	def test_delete_not_found(self):
		response = self.client.delete(reverse('delete', args=(config.UUID_NOT_FOUND,)))
		self.assertEqual(response.status_code, 404)
		self.assertEqual(json.loads(response.content), config.RESPONSE_NOT_FOUND)

	def test_delete_err(self):
		response = self.client.delete(reverse('delete', args=("err_uuid",)))
		self.assertEqual(response.status_code, 400)
		self.assertEqual(json.loads(response.content), config.RESPONSE_VALIDATION_FAILED)


class NodesTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		for batch in config.IMPORT_BATCHES:
			self.client.post(reverse('imports'), data=batch, content_type="application/json")

	def test_nodes_ok(self):
		response = self.client.get(reverse('nodes', args=(config.UUID_OK,)))
		self.assertEqual(response.status_code, 200)
		response_data = json.loads(response.content)
		self.assertEqual(deep_sort_children(response_data), deep_sort_children(config.EXPECTED_TREE))

	def test_nodes_not_found(self):
		response = self.client.get(reverse('nodes', args=(config.UUID_NOT_FOUND,)))
		self.assertEqual(response.status_code, 404)
		self.assertEqual(json.loads(response.content), config.RESPONSE_NOT_FOUND)

	def test_nodes_err(self):
		response = self.client.get(reverse('nodes', args=("err_uuid",)))
		self.assertEqual(response.status_code, 400)
		self.assertEqual(json.loads(response.content), config.RESPONSE_VALIDATION_FAILED)


class SalesTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		for batch in config.IMPORT_BATCHES:
			self.client.post(reverse('imports'), data=batch, content_type="application/json")

	def test_sales_ok(self):
		params = urllib.parse.urlencode({
			"date": "2022-02-04T00:00:00.000Z"
		})
		response = self.client.get(f"/sales?{params}")
		self.assertEqual(response.status_code, 200)

	def test_sales_err(self):
		params = urllib.parse.urlencode({
			"date": "2022.02.04 00:00:00"
		})
		response = self.client.get(f"/sales?{params}")
		self.assertEqual(response.status_code, 400)
		self.assertEqual(json.loads(response.content), config.RESPONSE_VALIDATION_FAILED)


class NodeStatisticTestCase(TestCase):
	def setUp(self):
		self.client = Client()
		self.params = urllib.parse.urlencode({
			"dateStart": "2022-02-01T00:00:00.000Z",
			"dateEnd": "2022-02-03T00:00:00.000Z"
		})
		for batch in config.IMPORT_BATCHES:
			self.client.post(reverse('imports'), data=batch, content_type="application/json")

	def test_stats_ok(self):
		response = self.client.get(f"/node/{config.UUID_OK}/statistic?{self.params}")
		self.assertEqual(response.status_code, 200)

	def test_stats_not_found(self):
		response = self.client.get(f"/node/{config.UUID_NOT_FOUND}/statistic?{self.params}")
		self.assertEqual(response.status_code, 404)
		self.assertEqual(json.loads(response.content), config.RESPONSE_NOT_FOUND)

	def test_stats_err(self):
		response = self.client.get(f"/node/err_uuid/statistic?{self.params}")
		self.assertEqual(response.status_code, 400)
		self.assertEqual(json.loads(response.content), config.RESPONSE_VALIDATION_FAILED)
