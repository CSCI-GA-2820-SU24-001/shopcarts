"""
Models for Shopcarts

The models for ShopcartItems are stored in this module
"""

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
    price = db.Column(db.Float())

    def __repr__(self):
        return f"<ShopcartItem {self.name} id=[{self.id}] shopcart_id=[{self.shopcart_id}]>"

    def __str__(self):
        return (
            f"{self.name}: {self.product_id}, {self.quantity}, {self.price}"
        )

    def serialize(self) -> dict:
        """Converts a ShopcartItem into a dictionary"""
        return {
            "id": self.id,
            "shopcart_id": self.shopcart_id,
            "name": self.name,
            "product_id": self.product_id,
            "quantity": int(self.quantity),
            "price": float(self.price),
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

            if isinstance(data["quantity"], int):
                self.quantity = data["quantity"]
            else:
                raise TypeError(
                    "Invalid type for int [quantity]: "
                    + str(type(data["quantity"]))
                )

            if isinstance(data["price"], (int, float)):
                self.price = data["price"]
            else:
                raise TypeError(
                    "Invalid type for int/float [price]: "
                    + str(type(data["price"]))
                )
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid ShopcartItem: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid ShopcartItem: body of request contained bad or no data "
                + str(error)
            ) from error

        return self

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
        return cls.query.filter(cls.product_id == product_id, cls.shopcart_id == shopcart_id).first()

    @classmethod
    def find_by_name(cls, name):
        """Returns all ShopcartItems with the given name

        Args:
            name (string): the name of the ShopcartItem you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).first()
