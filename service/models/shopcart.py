"""
Models for Shopcarts

The models for Shopcarts are stored in this module
"""

from .persistent_base import db, PersistentBase, DataValidationError
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
            "total_price": float(self.total_price),
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
                self.total_price = data["total_price"]
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
