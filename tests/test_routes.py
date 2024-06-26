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
                response.status_code, status.HTTP_201_CREATED, "Could not create test shopcart"
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
        """It should not get a Shopcart thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])
    
    def test_get_shopcart_list(self):
        """It should Get a list of Shopcarts"""
        self._create_shopcarts(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

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

    def test_update_shopcart_with_invalid_id(self):
        """It should not update a non-existing Shopcart"""
        # create a Shopcart to update
        test_shopcart = ShopcartFactory()

        resp = self.client.put(
            f"{BASE_URL}/{test_shopcart.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        print(resp.data.decode())
        self.assertIn(
            f"Shopcart with id '{test_shopcart.id}' was not found.",
            resp.data.decode(),
        )

    #####################################################################
    #  S H O P C A R T   I T E M   T E S T   C A S E S
    #####################################################################

    def test_delete_all_items_in_shopcart(self):
        """It should delete all items in a Shopcart"""
        # Create a shopcart with items
        test_shopcart = self._create_shopcarts(1)[0]
        test_shopcart.create()
        items = ShopcartItemFactory.create_batch(3, shopcart_id=test_shopcart.id)
        for item in items:
            item.create()
            test_shopcart.items.append(item)
        test_shopcart.update()

        # Ensure the shopcart has items
        self.assertEqual(len(test_shopcart.items), 3)

        # Delete all items
        response = self.client.delete(f"{BASE_URL}/{test_shopcart.id}/items")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Fetch the shopcart and ensure items are deleted
        updated_shopcart = Shopcart.find(test_shopcart.id)
        self.assertEqual(len(updated_shopcart.items), 0)
        self.assertEqual(updated_shopcart.total_price, 0)

    def test_delete_all_items_in_shopcart_with_invalid_id(self):
        """It should not delete all items in a non-existing Shopcart"""
        # Create a shopcart to delete
        test_shopcart = ShopcartFactory()

        resp = self.client.delete(f"{BASE_URL}/{test_shopcart.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        print(resp.data.decode())
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
        """It should return 415 if an Content-Type header is not present"""
        # create a Shopcart to update
        test_shopcart = self._create_shopcarts(1)[0]

        resp = self.client.put(f"{BASE_URL}/{test_shopcart.id}")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

