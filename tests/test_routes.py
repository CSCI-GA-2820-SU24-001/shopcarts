"""
Shopcart API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from tests.factories import ShopcartFactory, ShopcartItemFactory
from service.common import status
from service.models import db, Shopcart

# pylint: disable=duplicate-code
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/shopcarts"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestShopcartService(TestCase):
    """Shopcart Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_shopcarts(self, count: int = 1) -> list:
        """Factory method to create Shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopcartFactory()
            response = self.client.post(BASE_URL, json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Shopcart",
            )
            new_shopcart = response.get_json()
            test_shopcart.id = new_shopcart["id"]
            shopcarts.append(test_shopcart)
        return shopcarts

    def _create_items(self, shopcart_id, count: int = 1) -> list:
        """Factory method to create Items in bulk"""
        items = []
        for _ in range(count):
            test_item = ShopcartItemFactory(shopcart_id=shopcart_id)
            response = self.client.post(
                f"{BASE_URL}/{shopcart_id}/items", json=test_item.serialize()
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Item in Shopcart",
            )
            new_item = response.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return items

    ######################################################################
    #  S H O P C A R T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_shopcart(self):
        """It should get a single Shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_shopcart_when_shopcart_not_found(self):
        """It should not get a Shopcart that's not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_get_shopcart_list(self):
        """It should get a list of Shopcarts"""
        self._create_shopcarts(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_create_shopcart(self):
        """It should create a new Shopcart"""
        shopcart = ShopcartFactory()
        resp = self.client.post(
            BASE_URL, json=shopcart.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(
            new_shopcart["total_price"],
            shopcart.total_price,
            "Total Price does not match",
        )
        self.assertEqual(new_shopcart["items"], shopcart.items, "Items does not match")

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(
            new_shopcart["total_price"],
            shopcart.total_price,
            "Total Price does not match",
        )
        self.assertEqual(new_shopcart["items"], shopcart.items, "Items does not match")

    def test_update_shopcart(self):
        """It should update an existing Shopcart"""
        # create a Shopcart to update
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.client.post(BASE_URL, json=test_shopcart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = resp.get_json()
        new_shopcart["total_price"] = test_shopcart.total_price + 100
        new_shopcart_id = new_shopcart["id"]
        resp = self.client.put(f"{BASE_URL}/{new_shopcart_id}", json=new_shopcart)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(
            updated_shopcart["total_price"], test_shopcart.total_price + 100
        )

    def test_update_shopcart_when_shopcart_not_found(self):
        """It should not update a Shopcart that's not found"""
        # create a Shopcart to update
        test_shopcart = ShopcartFactory()

        resp = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

    def test_delete_shopcart(self):
        """It should Delete a Shopcart"""
        # get the id of an shopcart
        shopcart = self._create_shopcarts(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_query_shopcart_with_item_product_id(self):
        """It should return a list of all Shopcarts filtered by Item product_id"""
        # Create a shopcart with items
        shopcarts = self._create_shopcarts(2)
        items = self._create_items(shopcarts[0].id, 5)
        response = self.client.post(
            f"{BASE_URL}/{shopcarts[1].id}/items", json=items[0].serialize()
        )
        response = self.client.get(f"{BASE_URL}?product_id={items[0].product_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], shopcarts[0].id)
        self.assertEqual(data[1]["id"], shopcarts[1].id)
        response = self.client.get(f"{BASE_URL}?product_id={items[1].product_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], shopcarts[0].id)

    def test_query_shopcart_with_item_name(self):
        """It should return a list of all Shopcarts filtered by Item name"""
        # Create a shopcart with items
        shopcarts = self._create_shopcarts(2)
        items = self._create_items(shopcarts[0].id, 5)
        response = self.client.post(
            f"{BASE_URL}/{shopcarts[1].id}/items", json=items[0].serialize()
        )
        response = self.client.get(f"{BASE_URL}?name={items[0].name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], shopcarts[0].id)
        self.assertEqual(data[1]["id"], shopcarts[1].id)
        response = self.client.get(f"{BASE_URL}?name={items[1].name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], shopcarts[0].id)

    def test_query_shopcart_with_item_product_id_and_name(self):
        """It should return a list of all Shopcarts filtered by Item product_id and name"""
        # Create a shopcart with items
        shopcarts = self._create_shopcarts(2)
        items = self._create_items(shopcarts[0].id, 5)
        response = self.client.post(
            f"{BASE_URL}/{shopcarts[1].id}/items", json=items[0].serialize()
        )
        response = self.client.get(
            f"{BASE_URL}?product_id={items[0].product_id}&name={items[0].name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["id"], shopcarts[0].id)
        self.assertEqual(data[1]["id"], shopcarts[1].id)
        response = self.client.get(
            f"{BASE_URL}?product_id={items[1].product_id}&name={items[1].name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], shopcarts[0].id)

    def test_checkout_shopcart(self):
        """It should checkout a single Shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        self._create_items(shopcart.id, 5)

        response = self.client.get(f"{BASE_URL}/{shopcart.id}")
        updated_shopcart = response.get_json()

        response = self.client.get(f"{BASE_URL}/{shopcart.id}/checkout")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], shopcart.id)
        self.assertEqual(data["total_price"], updated_shopcart["total_price"])

    def test_checkout_shopcart_when_shopcart_not_found(self):
        """It should not checkout a Shopcart that's not found"""
        response = self.client.get(f"{BASE_URL}/0/checkout")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    #####################################################################
    #  S H O P C A R T   I T E M   T E S T   C A S E S
    #####################################################################

    def test_list_all_items_in_shopcart(self):
        """It should return a list of all Items in a Shopcart"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        self._create_items(shopcart.id, 2)

        # List all items
        response = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_list_all_items_in_shopcart_when_shopcart_not_found(self):
        """It should not list all Items in a Shopcart that's not found"""
        # Create a shopcart
        test_shopcart = ShopcartFactory()
        resp = self.client.get(f"{BASE_URL}/{test_shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

    def test_get_item_in_shopcart(self):
        """It should get a single Item in a Shopcart"""
        # get the id of an item in a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(test_shopcart.id, 1)[0]
        test_shopcart.items.append(test_item)
        test_shopcart.update()

        response = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_item.name)

    def test_get_item_in_shopcart_when_shopcart_not_found(self):
        """It should not get a Item from a Shopcart that's not found"""
        # Create a shopcart
        test_shopcart = ShopcartFactory()
        # Create an item but not in shopcart
        test_item = ShopcartItemFactory()
        response = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_get_item_in_shopcart_when_item_not_found(self):
        """It should not get a Item that's not found"""
        # Create a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        # Create an item but not in shopcart
        test_item = ShopcartItemFactory()
        response = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    def test_add_shopcart_item(self):
        """It should add an Item to a Shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        item = ShopcartItemFactory()

        response = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        data = response.get_json()
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["product_id"], item.product_id)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertEqual(data["price"], item.price)
        self.assertEqual(data["shopcart_id"], shopcart.id)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_item = response.get_json()
        self.assertEqual(new_item["name"], item.name)
        self.assertEqual(new_item["product_id"], item.product_id)
        self.assertEqual(new_item["quantity"], item.quantity)
        self.assertEqual(new_item["price"], item.price)
        self.assertEqual(new_item["shopcart_id"], shopcart.id)

    def test_add_existing_shopcart_item(self):
        """It should update the quantity if an existing Item is added to a Shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        item = ShopcartItemFactory()
        initial_quantity = item.quantity

        response = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        data = response.get_json()
        self.assertEqual(data["name"], item.name)
        self.assertEqual(data["quantity"], item.quantity)

        # Add the same item again with a different quantity
        updated_quantity = 3
        item.quantity = updated_quantity
        response = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the item's quantity has been updated
        updated_item = response.get_json()
        self.assertEqual(updated_item["name"], item.name)
        self.assertEqual(updated_item["quantity"], initial_quantity + updated_quantity)

        # Fetch the updated shopcart and verify the item's quantity
        response = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = response.get_json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], item.name)
        self.assertEqual(items[0]["quantity"], initial_quantity + updated_quantity)

    def test_add_shopcart_item_when_shopcart_not_found(self):
        """It should not delete all Items in a Shopcart that's not found"""
        # Create a shopcart to delete
        test_shopcart = ShopcartFactory()
        test_item = ShopcartItemFactory(shopcart=test_shopcart)
        resp = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

    def test_update_shopcart_item(self):
        """It should update an Item in a Shopcart"""
        # create a shopcart and item to update
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(test_shopcart.id, 1)[0]
        test_shopcart.items.append(test_item)
        test_shopcart.update()

        response = self.client.post(
            f"{BASE_URL}/{test_shopcart.id}/items", json=test_item.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the item
        updated_quantity = 999
        test_item.quantity = updated_quantity
        response = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}",
            json=test_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check quantity was updated
        updated_item = response.get_json()
        self.assertEqual(updated_item["name"], test_item.name)
        self.assertEqual(updated_item["quantity"], updated_quantity)

        # Fetch updated shopcart item and verify
        response = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.get_json()
        self.assertEqual(item["name"], test_item.name)
        self.assertEqual(item["quantity"], updated_quantity)

    def test_update_shopcart_item_when_shopcart_not_found(self):
        """It should not update an Item in a Shopcart that's not found"""
        # create a Shopcart and item to update
        test_shopcart = ShopcartFactory()
        test_item = ShopcartItemFactory()

        resp = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}",
            json=test_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

    def test_update_shopcart_item_when_item_not_found(self):
        """It should not update an Item in a Shopcart for an Item that's not found"""
        # create a Shopcart and item to update
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = ShopcartItemFactory()

        resp = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}",
            json=test_item.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Item with id '{test_item.id}' was not found in Shopcart with id '{test_shopcart.id}'.",
            resp.data.decode(),
        )

    def test_delete_all_items_in_shopcart(self):
        """It should delete all Items in a Shopcart"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        self._create_items(shopcart.id, 2)

        # Delete all items
        response = self.client.delete(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Fetch the shopcart and ensure items are deleted
        updated_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(updated_shopcart.items), 0)
        self.assertEqual(updated_shopcart.total_price, 0)

    def test_delete_all_items_in_shopcart_when_shopcart_not_found(self):
        """It should not delete all Items in a Shopcart that's not found"""
        # Create a shopcart to delete
        test_shopcart = ShopcartFactory()

        resp = self.client.delete(f"{BASE_URL}/{test_shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

    def test_delete_item_in_shopcart(self):
        """It should delete an Item from a Shopcart"""
        test_shopcart = self._create_shopcarts(1)[0]
        test_item = self._create_items(test_shopcart.id, 2)[0]

        # send delete request
        resp = self.client.delete(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # retrieve it back and make sure item is not there
        resp = self.client.get(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        # Fetch the shopcart and ensure item is deleted
        updated_shopcart = Shopcart.find(test_shopcart.id)
        self.assertEqual(len(updated_shopcart.items), 1)

    def test_delete_item_in_shopcart_when_shopcart_not_found(self):
        """It should not delete an Item in a Shopcart that's not found"""
        # Create a shopcart and item to delete
        test_shopcart = ShopcartFactory()
        test_item = ShopcartItemFactory()

        resp = self.client.delete(
            f"{BASE_URL}/{test_shopcart.id}/items/{test_item.id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

    def test_query_shopcart_items_with_product_id(self):
        """It should return a list of all Items in a Shopcart filtered by product_id"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        items = self._create_items(shopcart.id, 5)

        response = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items?product_id={items[0].product_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_id"], items[0].product_id)

    def test_query_shopcart_items_with_name(self):
        """It should return a list of all Items in a Shopcart filtered by name"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        items = self._create_items(shopcart.id, 5)

        response = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items?name={items[0].name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], items[0].name)

    def test_query_shopcart_items_with_product_id_and_name(self):
        """It should return a list of all Items in a Shopcart filtered by product_id and name"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        items = self._create_items(shopcart.id, 5)

        response = self.client.get(
            f"{BASE_URL}/{shopcart.id}/items?product_id={items[0].product_id}&name={items[0].name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_id"], items[0].product_id)
        self.assertEqual(data[0]["name"], items[0].name)

    ######################################################################
    #  U T I L I T Y   F U N C T I O N   T E S T   C A S E S
    ######################################################################

    def test_invalid_content_type(self):
        """It should return 415 if an invalid Content-Type header is present"""
        # create a Shopcart to update
        test_shopcart = self._create_shopcarts(1)[0]

        resp = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}", content_type="text/plain"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_missing_content_type(self):
        """It should return 415 if a Content-Type header is not present"""
        # create a Shopcart to update
        test_shopcart = self._create_shopcarts(1)[0]

        resp = self.client.put(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_bad_request(self):
        """It should not create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
