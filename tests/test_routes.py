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
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopcartFactory()
            response = self.client.post(BASE_URL, json=test_shopcart.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test shopcart",
            )
            new_shopcart = response.get_json()
            test_shopcart.id = new_shopcart["id"]
            shopcarts.append(test_shopcart)
        return shopcarts

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

    def test_get_shopcart_not_found(self):
        """It should not get a Shopcart that's not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
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
            float(new_shopcart["total_price"]),
            float(shopcart.total_price),
            "Total Price does not match",
        )
        self.assertEqual(new_shopcart["items"], shopcart.items, "Items does not match")

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(
            float(new_shopcart["total_price"]),
            float(shopcart.total_price),
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

    def test_update_shopcart_not_found(self):
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
        
    #####################################################################
    #  S H O P C A R T   I T E M   T E S T   C A S E S
    #####################################################################

    def test_list_all_items_in_shopcart(self):
        """It should return a list of all items in a Shopcart"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        items = ShopcartItemFactory.create_batch(2)

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=items[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=items[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # List all items
        response = self.client.get(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)

    def test_list_all_items_in_shopcart_not_found(self):
        """It should not list all items in a Shopcart that's not found"""
        # Create a shopcart
        test_shopcart = ShopcartFactory()
        resp = self.client.get(f"{BASE_URL}/{test_shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

    def test_add_shopcart_item(self):
        """It should add an Item to a Shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        item = ShopcartItemFactory()
        logging.debug("Test Item: %s", item.serialize())

        response = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=item.serialize(), content_type="application/json"
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

        # todo - uncomment when "get_shopcart_items" is implemented
        # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_item = response.get_json()[0]
        # self.assertEqual(new_item["name"], test_item.name)
        # self.assertEqual(new_item["product_id"], test_item.product_id)
        # self.assertEqual(new_item["quantity"], test_item.quantity)
        # self.assertEqual(new_item["price"], test_item.price)
        # self.assertEqual(new_item["shopcart_id"], shopcart.id)

    def test_add_existing_shopcart_item(self):
        """It should update the quantity if an existing item is added to a Shopcart"""
        shopcart = self._create_shopcarts(1)[0]
        item = ShopcartItemFactory()
        initial_quantity = item.quantity
        logging.debug("Test Item: %s", item.serialize())

        response = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=item.serialize(), content_type="application/json"
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
            f"{BASE_URL}/{shopcart.id}/items", json=item.serialize(), content_type="application/json"
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

    def test_add_shopcart_item_not_found(self):
        """It should not delete all items in a Shopcart that's not found"""
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

    def test_delete_all_items_in_shopcart(self):
        """It should delete all items in a Shopcart"""
        # Create a shopcart with items
        shopcart = self._create_shopcarts(1)[0]
        items = ShopcartItemFactory.create_batch(2)

        # Create item 1
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=items[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create item 2
        resp = self.client.post(
            f"{BASE_URL}/{shopcart.id}/items", json=items[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Delete all items
        response = self.client.delete(f"{BASE_URL}/{shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Fetch the shopcart and ensure items are deleted
        updated_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(updated_shopcart.items), 0)
        self.assertEqual(updated_shopcart.total_price, 0)

    def test_delete_all_items_in_shopcart_not_found(self):
        """It should not delete all items in a Shopcart that's not found"""
        # Create a shopcart to delete
        test_shopcart = ShopcartFactory()

        resp = self.client.delete(f"{BASE_URL}/{test_shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

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
