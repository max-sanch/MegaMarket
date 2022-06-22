from uuid import UUID

from shop_unit.models import ShopUnitType

UUID_OK = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
UUID_NOT_FOUND = "069cb8d7-bbdd-47d3-ad8f-82ef4c26d404"

UUID_CHILDREN_1 = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df2"
UUID_CHILDREN_2 = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df3"
UUID_CHILDREN_3 = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df4"

RESPONSE_NOT_FOUND = {"code": 404, "message": "Item not found"}
RESPONSE_VALIDATION_FAILED = {"code": 400, "message": "Validation Failed"}

IMPORT_OK = {
	"items": [
		{
			"type": "OFFER",
			"name": "jPhone 13",
			"id": "863e1a7a-1304-42ae-943b-179184c077e3",
			"parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
			"price": 79999
		},
		{
			"type": "CATEGORY",
			"name": "Смартфоны",
			"id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
			"parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
		},
		{
			"type": "CATEGORY",
			"name": "Товары",
			"id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
			"parentId": None
		},
		{
			"type": "OFFER",
			"name": "Xomiа Readme 10",
			"id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
			"parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
			"price": 59999
		}
	],
	"updateDate": "2022-02-01T12:00:00.000Z"
}

IMPORT_UPDATE_OK = {
	"items": [
		{
			"type": "CATEGORY",
			"name": "Товары",
			"id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
			"parentId": None
		}
	],
	"updateDate": "2022-02-01T12:00:01.000Z"
}

IMPORT_NOT_FOUND = {
	"items": [
		{
			"type": "OFFER",
			"name": "jPhone 13",
			"id": "863e1a7a-1304-42ae-943b-179184c077e3",
			"parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
			"price": 79999
		},
		{
			"type": "CATEGORY",
			"name": "Смартфоны",
			"id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
			"parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
		}
	],
	"updateDate": "2022-02-01T12:00:00.000Z"
}

IMPORT_TYPE_ERR_NAME = {
	"items": [
		{
			"type": "OFFER",
			"name": None,
			"id": "863e1a7a-1304-42ae-943b-179184c077e3",
			"parentId": None,
			"price": 79999
		}
	],
	"updateDate": "2022-02-01T12:00:00.000Z"
}

IMPORT_TYPE_ERR_PRICE = {
	"items": [
		{
			"type": "OFFER",
			"name": "jPhone 13",
			"id": "863e1a7a-1304-42ae-943b-179184c077e3",
			"parentId": None,
			"price": -2200
		}
	],
	"updateDate": "2022-02-01T12:00:00.000Z"
}

IMPORT_FORMAT_ERR_DATE = {
	"items": [
		{
			"type": "OFFER",
			"name": "jPhone 13",
			"id": "863e1a7a-1304-42ae-943b-179184c077e3",
			"parentId": None,
			"price": 79999
		}
	],
	"updateDate": "2022.02.01 12:00:00"
}

NODE_TREE_OK = {
	"id": UUID("069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"),
	"name": "Товары",
	"date": "2022-02-01T12:00:00.000Z",
	"parentId": None,
	"type": ShopUnitType.CATEGORY,
	"price": 69999,
	"children": [
		{
			"id": UUID("d515e43f-f3f6-4471-bb77-6b455017a2d2"),
			"name": "Смартфоны",
			"date": "2022-02-01T12:00:00.000Z",
			"parentId": UUID("069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"),
			"type": ShopUnitType.CATEGORY,
			"price": 69999,
			"children": [
				{
					"id": UUID("863e1a7a-1304-42ae-943b-179184c077e3"),
					"name": "jPhone 13",
					"date": "2022-02-01T12:00:00.000Z",
					"parentId": UUID("d515e43f-f3f6-4471-bb77-6b455017a2d2"),
					"type": ShopUnitType.OFFER,
					"price": 79999, "children": None
				},
				{
					"id": UUID("b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4"),
					"name": "Xomiа Readme 10",
					"date": '2022-02-01T12:00:00.000Z',
					"parentId": UUID("d515e43f-f3f6-4471-bb77-6b455017a2d2"),
					"type": ShopUnitType.OFFER,
					"price": 59999,
					"children": None
				}
			]
		}
	]
}

IMPORT_BATCHES = [
	{
		"items": [
			{
				"type": "CATEGORY",
				"name": "Товары",
				"id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
				"parentId": None
			}
		],
		"updateDate": "2022-02-01T12:00:00.000Z"
	},
	{
		"items": [
			{
				"type": "CATEGORY",
				"name": "Смартфоны",
				"id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
				"parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
			},
			{
				"type": "OFFER",
				"name": "jPhone 13",
				"id": "863e1a7a-1304-42ae-943b-179184c077e3",
				"parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
				"price": 79999
			},
			{
				"type": "OFFER",
				"name": "Xomiа Readme 10",
				"id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
				"parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
				"price": 59999
			}
		],
		"updateDate": "2022-02-02T12:00:00.000Z"
	},
	{
		"items": [
			{
				"type": "CATEGORY",
				"name": "Телевизоры",
				"id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
				"parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
			},
			{
				"type": "OFFER",
				"name": "Samson 70\" LED UHD Smart",
				"id": "98883e8f-0507-482f-bce2-2fb306cf6483",
				"parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
				"price": 32999
			},
			{
				"type": "OFFER",
				"name": "Phyllis 50\" LED UHD Smarter",
				"id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
				"parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
				"price": 49999
			}
		],
		"updateDate": "2022-02-03T12:00:00.000Z"
	},
	{
		"items": [
			{
				"type": "OFFER",
				"name": "Goldstar 65\" LED UHD LOL Very Smart",
				"id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
				"parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
				"price": 69999
			}
		],
		"updateDate": "2022-02-03T15:00:00.000Z"
	}
]

EXPECTED_TREE = {
	"type": "CATEGORY",
	"name": "Товары",
	"id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
	"price": 58599,
	"parentId": None,
	"date": "2022-02-03T15:00:00.000Z",
	"children": [
		{
			"type": "CATEGORY",
			"name": "Телевизоры",
			"id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
			"parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
			"price": 50999,
			"date": "2022-02-03T15:00:00.000Z",
			"children": [
				{
					"type": "OFFER",
					"name": "Samson 70\" LED UHD Smart",
					"id": "98883e8f-0507-482f-bce2-2fb306cf6483",
					"parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
					"price": 32999,
					"date": "2022-02-03T12:00:00.000Z",
					"children": None,
				},
				{
					"type": "OFFER",
					"name": "Phyllis 50\" LED UHD Smarter",
					"id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
					"parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
					"price": 49999,
					"date": "2022-02-03T12:00:00.000Z",
					"children": None
				},
				{
					"type": "OFFER",
					"name": "Goldstar 65\" LED UHD LOL Very Smart",
					"id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
					"parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
					"price": 69999,
					"date": "2022-02-03T15:00:00.000Z",
					"children": None
				}
			]
		},
		{
			"type": "CATEGORY",
			"name": "Смартфоны",
			"id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
			"parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
			"price": 69999,
			"date": "2022-02-02T12:00:00.000Z",
			"children": [
				{
					"type": "OFFER",
					"name": "jPhone 13",
					"id": "863e1a7a-1304-42ae-943b-179184c077e3",
					"parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
					"price": 79999,
					"date": "2022-02-02T12:00:00.000Z",
					"children": None
				},
				{
					"type": "OFFER",
					"name": "Xomiа Readme 10",
					"id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
					"parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
					"price": 59999,
					"date": "2022-02-02T12:00:00.000Z",
					"children": None
				}
			]
		},
	]
}
