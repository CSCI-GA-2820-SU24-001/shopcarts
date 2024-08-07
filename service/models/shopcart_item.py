"""
Models for Shopcarts

The models for ShopcartItems are stored in this module
"""

from decimal import Decimal
from .persistent_base import db, logger, PersistentBase, DataValidationError


######################################################################
#  S H O P C A R T   I T E M   M O D E L
######################################################################
class ShopcartItem(db.Model, PersistentBase):
    """
    Class that represents a ShopcartItem
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    shopcart_id = db.Column(
        db.Integer, db.ForeignKey("shopcart.id", ondelete="CASCADE"), nullable=False
    )
    product_id = db.Column(db.Integer)
    name = db.Column(db.String(64))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(scale=2))

    def __repr__(self):
        return f"<ShopcartItem {self.name} id=[{self.id}] shopcart_id=[{self.shopcart_id}]>"

    def __str__(self):
        return f"{self.name}: {self.product_id}, {self.quantity}, {self.price}"

    def serialize(self) -> dict:
        """Converts a ShopcartItem into a dictionary"""
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "name": self.name,
            "product_id": self.product_id,
            "quantity": int(self.quantity),
            "price": float(f"{self.price:.2f}"),
        }

    def deserialize(self, data):
        """
        Populates a ShopcartItem from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.shopcart_id = data["shopcart_id"]
            self.name = data["name"]
            self.product_id = data["product_id"]
            self.validate_quantity(data)
            self.validate_price(data)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid ShopcartItem: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid ShopcartItem: "
                + str(error)
            ) from error
        except ValueError as error:
            raise DataValidationError(
                "Invalid ShopcartItem: "
                + str(error)
            ) from error

        return self

    def validate_price(self, data):
        """
        Validates the price field.

        Args:
            data (dict): A dictionary containing the 'price' to be validated.
        """
        if "price" not in data or data["price"] is None:
            raise ValueError("Missing value for [price]")
        if not isinstance(data["price"], (int, float)):
            raise TypeError(
                "Invalid type for [price], must be a decimal: [ "
                + str(type(data["price"])) + "]"
            )
        if data["price"] < 0:
            raise ValueError(
                "Invalid value for [price], must be non-negative: [ "
                + str(data["price"]) + "]"
            )
        self.price = round(Decimal(data["price"]), 2)

    def validate_quantity(self, data):
        """
        Validates the quantity field.

        Args:
            data (dict): A dictionary containing the 'quantity' to be validated.
        """
        if "quantity" not in data or data["quantity"] is None:
            raise ValueError("Missing value for [quantity]")
        if not isinstance(data["quantity"], int):
            raise TypeError(
                "Invalid type for [quantity], must be an integer: [ "
                + str(type(data["quantity"]) + "]")
            )
        if data["quantity"] < 0:
            raise ValueError(
                "Invalid value for [quantity], must be non-negative: [ "
                + str(data["quantity"])
                + "]"
            )
        self.quantity = data["quantity"]

    ##################################################
    # Class Methods
    ##################################################

    @classmethod
    def find_by_shopcart_id(cls, shopcart_id):
        """Returns all ShopcartItems with the given shopcart_id

        Args:
            shopcart_id (int): the shopcart_id of the ShopcartItem you want to match
        """
        logger.info("Processing shopcart_id query for %s ...", shopcart_id)
        return cls.query.filter(cls.shopcart_id == shopcart_id).first()

    @classmethod
    def find_by_product_id(cls, product_id):
        """Returns all ShopcartItems with the given product_id

        Args:
            product_id (string): the product_id of the ShopcartItem you want to match
        """
        logger.info("Processing product_id query for %s", product_id)
        return cls.query.filter(cls.product_id == product_id).first()

    @classmethod
    def find_by_product_id_shopcart_id(cls, product_id, shopcart_id):
        """Returns all ShopcartItems with the given product_id and shopcart_id

        Args:
            product_id (string): the product_id of the ShopcartItem you want to match
            shopcart_id (string): the shopcart_id of the ShopcartItem you want to match
        """
        logger.info("Processing product_id query for %s", product_id)
        return cls.query.filter(
            cls.product_id == product_id, cls.shopcart_id == shopcart_id
        ).first()

    @classmethod
    def find_by_name(cls, name):
        """Returns all ShopcartItems with the given name

        Args:
            name (string): the name of the ShopcartItem you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).first()
