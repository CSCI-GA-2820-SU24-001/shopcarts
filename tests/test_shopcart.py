"""
Test cases for Shopcart Model
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
#        S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################
class TestShopcartModel(TestCaseBase):
    """Shopcart Model CRUD Tests"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_shopcart(self):
        """It should create a Shopcart and assert that it exists"""
        fake_shopcart = ShopcartFactory()
        # pylint: disable=unexpected-keyword-arg

        shopcart = Shopcart(
            total_price=fake_shopcart.total_price,
        )

        self.assertIsNotNone(shopcart)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.total_price, fake_shopcart.total_price)

    def test_add_a_shopcart(self):
        """It should create a Shopcart and add it to the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)

    def test_read_shopcart(self):
        """It should read a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()

        # Read it back
        found_shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(found_shopcart.id, shopcart.id)
        self.assertEqual(found_shopcart.total_price, shopcart.total_price)
        self.assertEqual(found_shopcart.items, [])

    def test_update_shopcart(self):
        """It should update a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)

        # Fetch it back
        shopcart = Shopcart.find(shopcart.id)
        shopcart.total_price = 250.00
        shopcart.update()

        # Fetch it back again
        shopcart = Shopcart.find(shopcart.id)
        self.assertEqual(shopcart.total_price, 250.00)

    def test_delete_a_shopcart(self):
        """It should delete a Shopcart from the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        shopcart = ShopcartFactory()
        shopcart.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(shopcart.id)
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 1)
        shopcart = shopcarts[0]
        shopcart.delete()
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 0)

    def test_list_all_shopcarts(self):
        """It should list all Shopcarts in the database"""
        shopcarts = Shopcart.all()
        self.assertEqual(shopcarts, [])
        for shopcart in ShopcartFactory.create_batch(5):
            shopcart.create()

        # Assert that there are 5 Shopcarts in the database
        shopcarts = Shopcart.all()
        self.assertEqual(len(shopcarts), 5)

    def test_serialize_a_shopcart(self):
        """It should serialize a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart_item = ShopcartItemFactory()
        shopcart.items.append(shopcart_item)
        serial_shopcart = shopcart.serialize()
        self.assertEqual(serial_shopcart["id"], shopcart.id)
        self.assertEqual(serial_shopcart["total_price"], float(shopcart.total_price))
        self.assertEqual(len(serial_shopcart["items"]), 1)
        items = serial_shopcart["items"]
        self.assertEqual(items[0]["id"], shopcart_item.id)
        self.assertEqual(items[0]["shopcart_id"], shopcart_item.shopcart_id)
        self.assertEqual(items[0]["product_id"], shopcart_item.product_id)
        self.assertEqual(items[0]["name"], shopcart_item.name)
        self.assertEqual(items[0]["quantity"], shopcart_item.quantity)
        self.assertEqual(items[0]["price"], float(shopcart_item.price))

    def test_deserialize_a_shopcart(self):
        """It should deserialize a Shopcart"""
        shopcart = ShopcartFactory()
        shopcart_item = ShopcartItemFactory()
        shopcart.items.append(shopcart_item)
        shopcart.create()
        serial_shopcart = shopcart.serialize()
        new_shopcart = Shopcart()
        new_shopcart.deserialize(serial_shopcart)
        self.assertNotEqual(new_shopcart, None)
        self.assertEqual(new_shopcart.id, None)
        self.assertEqual(new_shopcart.total_price, shopcart.total_price)
        self.assertNotEqual(new_shopcart.items, None)
        self.assertEqual(new_shopcart.items[0].name, shopcart_item.name)

    def test_models_repr_str(self):
        """It should have the correct repr and str for Shopcart"""
        shopcart = Shopcart()
        self.assertEqual(
            shopcart.__repr__(),  # pylint: disable=unnecessary-dunder-call
            f"<Shopcart id=[{shopcart.id}]>",
        )

    @patch("service.models.db.session.commit")
    def test_add_shopcart_failed(self, exception_mock):
        """It should not create a Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.create)

    @patch("service.models.db.session.commit")
    def test_update_shopcart_failed(self, exception_mock):
        """It should not update a Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.update)

    def test_update_shopcart_no_id(self):
        """It should not update a Shopcart with no id"""
        shopcart = ShopcartFactory()
        shopcart.id = None
        self.assertRaises(DataValidationError, shopcart.update)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_failed(self, exception_mock):
        """It should not delete a Shopcart on database error"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.delete)


########################################################################
# T E S T   D E S E R I A L I Z E   E X C E P T I O N   H A N D L E R S
########################################################################
class TestDeserializeExceptionHandlers(TestCaseBase):
    """Shopcart Model Deserialize Exception Handlers"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_deserialize_missing_total_price(self):
        """It should not deserialize a Shopcart with missing total_price"""
        data = {"items": [{"shopcart_id": 1, "name": "Product1", "product_id": 101, "quantity": 2, "price": 20.0}]}
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_deserialize_missing_items(self):
        """It should deserialize a Shopcart with missing items"""
        data = {"total_price": 100.0}
        shopcart = Shopcart()
        shopcart.deserialize(data)
        self.assertEqual(shopcart.total_price, 100.0)
        self.assertEqual(len(shopcart.items), 0)

    def test_deserialize_bad_total_price(self):
        """It should not deserialize a bad total_price attribute"""
        data = ShopcartFactory().serialize()
        data["total_price"] = "fifty"
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_deserialize_bad_item(self):
        """It should not deserialize a bad item attribute"""
        data = ShopcartFactory().serialize()
        data["items"] = [{"shopcart_id": 1, "name": "Product1", "product_id": 101, "quantity": "two", "price": 20.0}]
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_deserialize_invalid_attribute(self):
        """It should not deserialize a Shopcart with invalid attributes"""
        data = ShopcartFactory().serialize()

        # Temporarily override the __setattr__ method to simulate AttributeError
        original_setattr = Shopcart.__setattr__

        def mock_setattr(self, name, value):
            if name == "total_price":
                raise AttributeError("Simulated AttributeError for testing")
            original_setattr(self, name, value)

        Shopcart.__setattr__ = mock_setattr
        shopcart = Shopcart()
        try:
            self.assertRaises(DataValidationError, shopcart.deserialize, data)
        finally:
            Shopcart.__setattr__ = original_setattr  # Restore original method


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestCaseBase):
    """Shopcart Model Exception Handlers"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    @patch("service.models.db.session.commit")
    def test_create_shopcart_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.create)

    @patch("service.models.db.session.commit")
    def test_update_shopcart_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.update)

    @patch("service.models.db.session.commit")
    def test_delete_shopcart_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        shopcart = ShopcartFactory()
        self.assertRaises(DataValidationError, shopcart.delete)
