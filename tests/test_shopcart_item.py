"""
Test cases for ShopcartItem Model
"""

import logging
import os
from unittest import TestCase
from unittest.mock import patch
from decimal import Decimal
from wsgi import app
from service.models import Shopcart, ShopcartItem, DataValidationError, db
from tests.factories import ShopcartFactory, ShopcartItemFactory

# pylint: disable=duplicate-code
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  B A S E   T E S T   C A S E S
######################################################################
class TestCaseBase(TestCase):
    """Base Test Case for common setup"""

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
#     S H O P C A R T   I T E M   M O D E L   T E S T   C A S E S
######################################################################
class TestShopcartItemModel(TestCaseBase):
    """ShopcartItem Model CRUD Tests"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_shopcart_item(self):
        """It should create a Shopcart with a ShopcartItem and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart_item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(shopcart_item)
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 1)
        self.assertEqual(new_shopcart.items[0].name, shopcart_item.name)

        shopcart_item2 = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(shopcart_item2)
        shopcart.update()
        new_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(new_shopcart.items), 2)
        self.assertEqual(new_shopcart.items[1].name, shopcart_item2.name)

    def test_read_shopcart_item(self):
        """It should read a ShopcartItem from the database"""
        shopcart_item = ShopcartItemFactory()
        shopcart_item.create()

        # Read it back
        found_shopcart_item = ShopcartItem.find(shopcart_item.id)
        self.assertEqual(found_shopcart_item.id, shopcart_item.id)
        self.assertEqual(found_shopcart_item.quantity, shopcart_item.quantity)

    def test_update_shopcart_item(self):
        """It should update a ShopcartItem"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart_item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(shopcart_item)
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        old_item = shopcart.items[0]
        self.assertEqual(old_item.name, shopcart_item.name)

        # Change the name
        old_item.name = "i-10"
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        shopcart_item = shopcart.items[0]
        self.assertEqual(shopcart_item.name, "i-10")

    def test_delete_shopcart_item(self):
        """It should delete a ShopcartItem"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart_item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(shopcart_item)
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        shopcart_item = shopcart.items[0]
        shopcart_item.delete()
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(len(shopcart.items), 0)

    def test_list_all_shopcart_items(self):
        """It should list all ShopcartItems in the database"""
        shopcart_items = ShopcartItem.all()
        self.assertEqual(shopcart_items, [])
        for shopcart_item in ShopcartItemFactory.create_batch(5):
            shopcart_item.create()

        # Assert that there are 5 ShopcartItems in the database
        shopcart_items = ShopcartItem.all()
        self.assertEqual(len(shopcart_items), 5)

    def test_serialize_a_shopcart_item(self):
        """It should serialize a ShopcartItem"""
        shopcart_item = ShopcartItemFactory()
        serial_shopcart_item = shopcart_item.serialize()
        self.assertEqual(serial_shopcart_item["id"], shopcart_item.id)
        self.assertEqual(serial_shopcart_item["shopcart_id"], shopcart_item.shopcart_id)
        self.assertEqual(serial_shopcart_item["product_id"], shopcart_item.product_id)
        self.assertEqual(serial_shopcart_item["name"], shopcart_item.name)
        self.assertEqual(serial_shopcart_item["quantity"], shopcart_item.quantity)
        self.assertEqual(serial_shopcart_item["price"], shopcart_item.price)

    def test_deserialize_a_shopcart_item(self):
        """It should deserialize a ShopcartItem"""
        data = ShopcartItemFactory().serialize()
        shopcart_item = ShopcartItem()
        shopcart_item.deserialize(data)
        self.assertNotEqual(shopcart_item, None)
        self.assertEqual(shopcart_item.id, None)
        self.assertEqual(shopcart_item.shopcart_id, data["shopcart_id"])
        self.assertEqual(shopcart_item.product_id, data["product_id"])
        self.assertEqual(shopcart_item.name, data["name"])
        self.assertEqual(shopcart_item.quantity, int(data["quantity"]))
        self.assertEqual(shopcart_item.price, round(Decimal(data["price"]), 2))

    def test_models_repr_str(self):
        """It should have the correct repr and str for ShopcartItem"""
        shopcart_item = ShopcartItem()
        self.assertEqual(
            shopcart_item.__repr__(),  # pylint: disable=unnecessary-dunder-call
            f"<ShopcartItem {shopcart_item.name} id=[{shopcart_item.id}] shopcart_id=[{shopcart_item.shopcart_id}]>",
        )
        self.assertEqual(
            shopcart_item.__str__(),  # pylint: disable=unnecessary-dunder-call
            f"{shopcart_item.name}: {shopcart_item.product_id}, {shopcart_item.quantity}, {shopcart_item.price}",
        )

    @patch("service.models.db.session.commit")
    def test_add_shopcart_item_failed(self, exception_mock):
        """It should not create a ShopcartItem on database error"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.create)

    @patch("service.models.db.session.commit")
    def test_update_shopcart_item_failed(self, exception_mock):
        """It should not update a ShopcartItem on database error"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.update)

    def test_update_shopcart_item_no_id(self):
        """It should not update a ShopcartItem with no id"""
        shopcart_item = ShopcartItemFactory()
        shopcart_item.id = None
        self.assertRaises(DataValidationError, shopcart_item.update)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_item_failed(self, exception_mock):
        """It should not delete a ShopcartItem on database error"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.delete)


########################################################################
# T E S T   D E S E R I A L I Z E   E X C E P T I O N   H A N D L E R S
########################################################################
class TestDeserializeExceptionHandlers(TestCaseBase):
    """ShopcartItem Model Deserialize Exception Handlers"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_deserialize_missing_shopcart_id(self):
        """It should not deserialize a ShopcartItem with missing shopcart_id"""
        data = {"name": "Product1", "product_id": 101, "quantity": 2, "price": 20.0}
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

    def test_deserialize_missing_name(self):
        """It should not deserialize a ShopcartItem with missing name"""
        data = {"shopcart_id": 1, "product_id": 101, "quantity": 2, "price": 20.0}
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

    def test_deserialize_missing_product_id(self):
        """It should not deserialize a ShopcartItem with missing product_id"""
        data = {"shopcart_id": 1, "name": "Product1", "quantity": 2, "price": 20.0}
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

    def test_deserialize_missing_quantity(self):
        """It should not deserialize a ShopcartItem with missing quantity"""
        data = {"shopcart_id": 1, "name": "Product1", "product_id": 101, "price": 20.0}
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

    def test_deserialize_missing_price(self):
        """It should not deserialize a ShopcartItem with missing price"""
        data = {"shopcart_id": 1, "name": "Product1", "product_id": 101, "quantity": 2}
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

    def test_deserialize_bad_quantity(self):
        """It should not deserialize a bad quantity attribute"""
        data = ShopcartItemFactory().serialize()
        data["quantity"] = "two"
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

        data["quantity"] = -1
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

    def test_deserialize_bad_price(self):
        """It should not deserialize a bad price attribute"""
        data = ShopcartItemFactory().serialize()
        data["price"] = "twenty"
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

        data["price"] = -1
        shopcart_item = ShopcartItem()
        self.assertRaises(DataValidationError, shopcart_item.deserialize, data)

    def test_deserialize_invalid_attribute(self):
        """It should not deserialize a ShopcartItem with invalid attributes"""
        data = ShopcartItemFactory().serialize()

        # Temporarily override the __setattr__ method to simulate AttributeError
        original_setattr = ShopcartItem.__setattr__

        def mock_setattr(self, name, value):
            if name == "name":
                raise AttributeError("Simulated AttributeError for testing")
            original_setattr(self, name, value)

        ShopcartItem.__setattr__ = mock_setattr
        shopcart_item = ShopcartItem()
        try:
            self.assertRaises(DataValidationError, shopcart_item.deserialize, data)
        finally:
            ShopcartItem.__setattr__ = original_setattr  # Restore original method


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestCaseBase):
    """ShopcartItem Model Exception Handlers"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    @patch("service.models.db.session.commit")
    def test_create_shopcart_item_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.create)

    @patch("service.models.db.session.commit")
    def test_update_shopcart_item_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.update)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_item_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        shopcart_item = ShopcartItemFactory()
        self.assertRaises(DataValidationError, shopcart_item.delete)


######################################################################
#  Q U E R Y   T E S T   C A S E S
######################################################################
class TestModelQueries(TestCaseBase):
    """ShopcartItem Model Query Tests"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_find_shopcart_item_by_name(self):
        """It should find a ShopcartItem by name"""
        for shopcart_item in ShopcartItemFactory.create_batch(5):
            shopcart_item.create()

        # Assert that there are 5 ShopcartItems in the database
        shopcart_items = ShopcartItem.all()
        self.assertEqual(len(shopcart_items), 5)

        # find the 2nd shopcartItem in the list
        shopcart_item = ShopcartItem.find_by_name(shopcart_items[1].name)
        self.assertEqual(shopcart_item.id, shopcart_items[1].id)
        self.assertEqual(shopcart_item.quantity, shopcart_items[1].quantity)

    def test_find_shopcart_item_by_product_id(self):
        """It should find a ShopcartItem by product ID"""
        for shopcart_item in ShopcartItemFactory.create_batch(5):
            shopcart_item.create()

        # Assert that there are 5 ShopcartItems in the database
        shopcart_items = ShopcartItem.all()
        self.assertEqual(len(shopcart_items), 5)

        # find the 2nd shopcartItem in the list
        shopcart_item = ShopcartItem.find_by_product_id(shopcart_items[1].product_id)
        self.assertEqual(shopcart_item.id, shopcart_items[1].id)
        self.assertEqual(shopcart_item.quantity, shopcart_items[1].quantity)

    def test_find_shopcart_item_by_shopcart_id(self):
        """It should find a ShopcartItem by shopcart ID"""
        shopcart = ShopcartFactory()
        shopcart_item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(shopcart_item)
        shopcart.create()

        # Read it back
        found_shopcart_item = ShopcartItem.find_by_shopcart_id(shopcart.id)
        self.assertEqual(found_shopcart_item.id, shopcart_item.id)
        self.assertEqual(found_shopcart_item.quantity, shopcart_item.quantity)

    def test_find_shopcart_item_by_product_id_shopcart_id(self):
        """It should find a ShopcartItem by product ID and shopcart ID"""
        shopcart = ShopcartFactory()
        shopcart_item = ShopcartItemFactory(shopcart=shopcart)
        shopcart.items.append(shopcart_item)
        shopcart.create()

        # Read it back
        found_shopcart_item = ShopcartItem.find_by_product_id_shopcart_id(
            shopcart_item.product_id, shopcart.id
        )
        self.assertEqual(found_shopcart_item.id, shopcart_item.id)
        self.assertEqual(found_shopcart_item.quantity, shopcart_item.quantity)
