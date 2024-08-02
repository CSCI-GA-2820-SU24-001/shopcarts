"""
Models for Shopcarts

The models for Shopcarts are stored in this module
"""

from decimal import Decimal
from .persistent_base import db, logger, PersistentBase, DataValidationError
from .shopcart_item import ShopcartItem


######################################################################
#  S H O P C A R T    M O D E L
######################################################################
class Shopcart(db.Model, PersistentBase):
    """
    Class that represents a Shopcart
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Numeric(scale=2))
    items = db.relationship("ShopcartItem", backref="shopcart", passive_deletes=True)

    def __repr__(self):
        return f"<Shopcart id=[{self.id}]>"

    def serialize(self) -> dict:
        """Converts a Shopcart into a dictionary"""
        shopcart = {
            "id": self.id,
            "total_price": float(f"{self.total_price:.2f}"),
            "items": [],
        }
        for item in self.items:
            shopcart["items"].append(item.serialize())
        return shopcart

    def deserialize(self, data):
        """
        Populates a Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            if isinstance(data["total_price"], (int, float)):
                if data["total_price"] < 0:
                    raise ValueError(
                        "Invalid value for [total_price], must be non-negative: "
                        + str(data["total_price"])
                    )
                self.total_price = round(Decimal(data["total_price"]), 2)
            else:
                raise TypeError(
                    "Invalid type for int/float [total_price]: "
                    + str(type(data["total_price"]))
                )

            item_list = data.get("items")
            if item_list:
                for json_item in item_list:
                    item = ShopcartItem()
                    item.deserialize(json_item)
                    self.items.append(item)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Shopcart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data "
                + str(error)
            ) from error
        except ValueError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

    def calculate_total_price(self):
        """Update the total price of a ShopCart"""
        total_price = 0
        for item in self.items:
            if item.price is not None and item.quantity is not None:
                total_price += item.price * item.quantity

        self.total_price = total_price
        self.update()

    ##################################################
    # Class Methods
    ##################################################

    @classmethod
    def find_by_item_product_id(cls, product_id):
        """Returns all Shopcarts containing ShopcartItems with the given product_id

        Args:
            product_id (string): the product_id of the ShopcartItem you want to match
        """
        logger.info(
            "Processing query for shopcarts containing items with product_id %s",
            product_id,
        )

        items = ShopcartItem.query.filter(ShopcartItem.product_id == product_id).all()
        shopcarts = [item.shopcart_id for item in items]

        return cls.query.filter(cls.id.in_(shopcarts)).all()

    @classmethod
    def find_by_item_name(cls, name):
        """Returns all Shopcarts containing ShopcartItems with the given name

        Args:
            name (string): the name of the ShopcartItem you want to match
        """
        logger.info(
            "Processing query for shopcarts containing items with name %s", name
        )

        items = ShopcartItem.query.filter(ShopcartItem.name == name).all()
        shopcarts = [item.shopcart_id for item in items]

        return cls.query.filter(cls.id.in_(shopcarts)).all()
