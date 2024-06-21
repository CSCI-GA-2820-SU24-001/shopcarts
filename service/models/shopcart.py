"""
Models for Shopcarts

The models for Shopcarts are stored in this module
"""

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
    total_price = db.Column(db.Float())
    items = db.relationship("ShopcartItem", backref="shopcart", passive_deletes=True)

    def __repr__(self):
        return f"<Shopcart {self.name} id=[{self.id}]>"

    def serialize(self) -> dict:
        """Converts a Shopcart into a dictionary"""
        shopcart = {
            "id": self.id,
            "total_price": float(self.total_price),
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
            self.id = data["id"]
            self.total_price = data["total_price"]
            item_list = data.get("items")
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

        return self

    ##################################################
    # Class Methods
    ##################################################
    @classmethod
    def all(cls):
        """Returns all of the Shopcarts in the database"""
        logger.info("Processing all Shopcarts")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Shopcart by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)
