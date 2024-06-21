"""
Test cases for ShopcartItem Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Shopcart, ShopcartItem, DataValidationError, db
from tests.factories import ShopcartFactory, ShopcartItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#        A D D R E S S   M O D E L   T E S T   C A S E S
######################################################################
class TestShopcartItem(TestCase):
    """ShopcartItem Model Test Cases"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Shopcart).delete()  # clean up the last tests
        db.session.query(ShopcartItem).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_shopcart_item(self):
        """It should create a Shopcart with an Item and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(item)
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 1)
        self.assertEqual(new_shopcart.items[0].name, item.name)

        item2 = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(item2)
        shopcart.update()
        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 2)
        self.assertEqual(new_shopcart.items[1].name, item2.name)

    def test_read_shopcart_item(self):
        """It should read a Shopcart Item from the database"""
        shopcart_item = ShopcartItemFactory()
        shopcart_item.create()

        # Read it back
        found_shopcart_item = ShopcartItem.find(shopcart_item.id)
        self.assertEqual(found_shopcart_item.id, shopcart_item.id)
        self.assertEqual(found_shopcart_item.quantity, shopcart_item.quantity)

    def test_list_all_shopcart_items(self):
        """It should list all Shopcart Items in the database"""
        shopcart_items = ShopcartItem.all()
        self.assertEqual(shopcart_items, [])
        for shopcart_item in ShopcartItemFactory.create_batch(5):
            shopcart_item.create()

        # Assert that there are 5 Shopcart Items in the database
        shopcart_items = ShopcartItem.all()
        self.assertEqual(len(shopcart_items), 5)

    def test_update_shopcart_item(self):
        """It should update a Shopcart Item"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(item)
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        old_item = shopcart.items[0]
        print("%r", old_item)
        self.assertEqual(old_item.name, item.name)

        # Change the name
        old_item.name = "i-10"
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        item = shopcart.items[0]
        self.assertEqual(item.name, "i-10")

    def test_delete_shopcart_item(self):
        """It should delete a Shopcart Item"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(item)
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        item = shopcart.items[0]
        item.delete()
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(shopcart.items), 0)

    def test_serialize_a_shopcart_item(self):
        """It should serialize a Shopcart Item"""
        shopcart_item = ShopcartItemFactory()
        serial_shopcart_item = shopcart_item.serialize()
        self.assertEqual(serial_shopcart_item["id"], shopcart_item.id)
        self.assertEqual(serial_shopcart_item["shopcart_id"], shopcart_item.shopcart_id)
        self.assertEqual(serial_shopcart_item["product_id"], shopcart_item.product_id)
        self.assertEqual(serial_shopcart_item["name"], shopcart_item.name)
        self.assertEqual(serial_shopcart_item["quantity"], shopcart_item.quantity)
        self.assertEqual(serial_shopcart_item["price"], float(shopcart_item.price))

    def test_deserialize_a_shopcart_item(self):
        """It should deserialize a Shopcart Item"""
        shopcart_item = ShopcartItemFactory()
        shopcart_item.create()
        new_shopcart_item = ShopcartItem()
        new_shopcart_item.deserialize(shopcart_item.serialize())
        self.assertEqual(new_shopcart_item.id, shopcart_item.id)
        self.assertEqual(new_shopcart_item.shopcart_id, shopcart_item.shopcart_id)
        self.assertEqual(new_shopcart_item.product_id, shopcart_item.product_id)
        self.assertEqual(new_shopcart_item.name, shopcart_item.name)
        self.assertEqual(new_shopcart_item.quantity, shopcart_item.quantity)
        self.assertEqual(new_shopcart_item.price, float(shopcart_item.price))

    def test_find_shopcart_item_by_name(self):
        """It should find a Shopcart Item by name"""
        shopcart_item = ShopcartItemFactory()
        shopcart_item.create()
        item_name = shopcart_item.name

        # Read it back
        found_shopcart_item = ShopcartItem.find_by_name(item_name)
        self.assertEqual(found_shopcart_item.id, shopcart_item.id)
        self.assertEqual(found_shopcart_item.quantity, shopcart_item.quantity)

    def test_find_shopcart_item_by_product_id(self):
        """It should find a Shopcart Item by product ID"""
        shopcart_item = ShopcartItemFactory()
        shopcart_item.create()
        product_id = shopcart_item.product_id

        # Read it back
        found_shopcart_item = ShopcartItem.find_by_product_id(product_id)
        self.assertEqual(found_shopcart_item.id, shopcart_item.id)
        self.assertEqual(found_shopcart_item.quantity, shopcart_item.quantity)

    def test_find_shopcart_item_by_shopcart_id(self):
        """It should find a Shopcart Item by shopcart ID"""
        shopcart = ShopcartFactory()
        shopcart_item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(shopcart_item)
        shopcart.create()
        shopcart_id = shopcart_item.shopcart_id

        # Read it back
        found_shopcart_item = ShopcartItem.find_by_shopcart_id(shopcart_id)
        self.assertEqual(found_shopcart_item.id, shopcart_item.id)
        self.assertEqual(found_shopcart_item.quantity, shopcart_item.quantity)

    @patch("service.models.db.session.commit")
    def test_update_shopcart_item_failed(self, exception_mock):
        """It should not update a Shopcart Item on database error"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.update)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_item_failed(self, exception_mock):
        """It should not delete a Shopcart Item on database error"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.delete)

    def test_deserialize_with_key_error(self):
        """It should not deserialize a Shopcart Item with a KeyError"""
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not deserialize a Shopcart Item with a TypeError"""
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, [])

    def test_deserialize_shopcart_item_key_error(self):
        """It should not deserialize a Shopcart Item with a KeyError"""
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, {})

    def test_deserialize_shopcart_item_type_error(self):
        """It should not deserialize a Shopcart Item with a TypeError"""
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, [])

    @patch("service.models.db.session.commit")
    def test_create_shopcart_item_exception(self, exception_mock):
        """It should handle exception when creating a Shopcart Item"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.create)

    @patch("service.models.db.session.commit")
    def test_update_shopcart_item_exception(self, exception_mock):
        """It should handle an exception when updating a Shopcart Item"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.update)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_item_exception(self, exception_mock):
        """It should handle an exception when deleting a Shopcart Item"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.delete)
