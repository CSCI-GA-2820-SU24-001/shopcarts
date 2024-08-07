######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Shopcart Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Shopcarts and Shopcart Items
"""

from flask import current_app as app  # Import Flask application
from flask_restx import Resource, reqparse, fields
from service.models import Shopcart, ShopcartItem
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for Shopcarts service"""
    return app.send_static_file("index.html")


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


# Define the models so that the docs reflect what can be sent
create_shopcartItem_model = api.model(
    "ShopcartItem",
    {
        "shopcart_id": fields.Integer(required=True, description="ID of the shopcart"),
        "name": fields.String(required=True, description="Name of the shopcart item"),
        "product_id": fields.Integer(required=True, description="ID of the product"),
        "quantity": fields.Integer(
            required=True, description="Quantity of shopcart item"
        ),
        "price": fields.Float(required=True, description="Price of the product"),
    },
)

shopcartItem_model = api.inherit(
    "ShopcartItemModel",
    create_shopcartItem_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The unique ID of the shopcart item assigned internally by the service",
        ),
        "shopcart_id": fields.Integer(
            readOnly=True,
            description="The ID of the shopcart to which the shopcart item belongs",
        ),
    },
)

create_shopcart_model = api.model(
    "Shopcart",
    {
        "total_price": fields.Float(
            required=True, description="Total price of the shopcart"
        ),
        "items": fields.List(
            fields.Nested(shopcartItem_model),
            required=False,
            description="Items in the shopcart",
        ),
    },
)

shopcart_model = api.inherit(
    "ShopcartModel",
    create_shopcart_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The unique ID of the shopcart assigned internally by the service",
        ),
    },
)


# query string arguments
shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument(
    "product_id",
    type=int,
    location="args",
    required=False,
    help="Product ID of the Items in the Shopcart",
)
shopcart_args.add_argument(
    "name",
    type=str,
    location="args",
    required=False,
    help="Name of the Items in the Shopcart",
)

shopcartItem_args = reqparse.RequestParser()
shopcartItem_args.add_argument(
    "product_id",
    type=int,
    location="args",
    required=False,
    help="Product ID of the Item",
)
shopcartItem_args.add_argument(
    "name",
    type=str,
    location="args",
    required=False,
    help="Name of the Item",
)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /shopcarts/{id}
######################################################################
@api.route("/shopcarts/<int:shopcart_id>")
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartResource(Resource):
    """
    ShopcartResource class

    Allows the manipulation of a single Shopcart
    GET /shopcarts/{id} - Returns a Shopcart with the id
    PUT /shopcarts/{id} - Update a Shopcart with the id
    DELETE /shopcarts/{id} -  Deletes a Shopcart with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("get_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.marshal_with(shopcart_model)
    def get(self, shopcart_id):
        """
        Retrieve a single Shopcart

        This endpoint will return a Shopcart based on it's id
        """
        app.logger.info("Request to retrieve Shopcart with id [%s]", shopcart_id)

        # Attempt to find the Shopcart and abort if not found
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )

        app.logger.info("Returning Shopcart with id [%s]", shopcart_id)

        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING SHOPCART
    # ------------------------------------------------------------------
    @api.doc("update_shopcarts")
    @api.response(404, "Shopcart not found")
    @api.response(400, "The posted Shopcart data was not valid")
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model)
    def put(self, shopcart_id):
        """
        Update a Shopcart

        This endpoint will update an Shopcart based on the body that is posted
        """
        app.logger.info("Request to update Shopcart with id [%s]", shopcart_id)

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )

        app.logger.info("Processing: %s", api.payload)

        # Update from the json in the body of the request
        shopcart.deserialize(api.payload)
        shopcart.id = shopcart_id
        shopcart.update()

        app.logger.info("Shopcart with id [%s] updated!", shopcart_id)

        return shopcart.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("delete_shopcarts")
    @api.response(204, "Shopcart deleted")
    def delete(self, shopcart_id):
        """
        Delete a Shopcart

        This endpoint will delete a Shopcart based on its id
        """
        app.logger.info("Request to delete Shopcart with id [%s]", shopcart_id)

        # Attempt to find the Shopcart and abort if not found
        shopcart = Shopcart.find(shopcart_id)
        if shopcart:
            shopcart.delete()
            app.logger.info("Shopcart with id [%s] deleted!", shopcart_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /shopcarts
######################################################################
@api.route("/shopcarts", strict_slashes=False)
class ShopcartCollection(Resource):
    """Handles all interactions with collections of Shopcarts"""

    # ------------------------------------------------------------------
    # LIST ALL SHOPCARTS
    # ------------------------------------------------------------------
    @api.doc("list_shopcarts")
    @api.expect(shopcart_args, validate=True)
    @api.marshal_list_with(shopcart_model)
    def get(self):
        """Returns all of the Shopcarts"""
        app.logger.info("Request for Shopcarts list")

        # Get the query parameters
        args = shopcart_args.parse_args()
        product_id = args.get("product_id")
        name = args.get("name")

        shopcarts = []
        if product_id:
            app.logger.info("Filtering by product ID [%s]", product_id)
            shopcarts = Shopcart.find_by_item_product_id(product_id)
        elif name:
            app.logger.info("Filtering by product name [%s]", name)
            shopcarts = Shopcart.find_by_item_name(name)
        else:
            shopcarts = Shopcart.all()
            app.logger.info("Returning unfiltered list")
        shopcarts = [shopcart.serialize() for shopcart in shopcarts]

        app.logger.info("Returning [%d] shopcarts", len(shopcarts))

        return shopcarts, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW SHOPCART
    # ------------------------------------------------------------------
    @api.doc("create_shopcarts")
    @api.response(400, "The posted Shopcart data was not valid")
    @api.expect(create_shopcart_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self):
        """
        Creates a Shopcart

        This endpoint will create an Shopcart based the data on the body that is posted
        """
        app.logger.info("Request to create a Shopcart")
        app.logger.info("Processing: %s", api.payload)

        # Create the shopcart
        shopcart = Shopcart()
        shopcart.deserialize(api.payload)
        shopcart.create()

        app.logger.info("Shopcart with id [%s] saved!", shopcart.id)

        # Return the location of the new item
        location_url = api.url_for(ShopcartResource, shopcart_id=shopcart.id, _external=True)

        return shopcart.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /shopcarts/{id}/checkout
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/checkout")
@api.param("shopcart_id", "The Shopcart identifier")
class CheckoutResource(Resource):
    """Checkout action on a Shopcart"""

    @api.doc("checkout_shopcarts")
    @api.response(404, "Shopcart not found")
    def get(self, shopcart_id):
        """
        Checkout a Shopcart

        This endpoint will checkout a Shopcart based on its id
        """
        app.logger.info("Request to checkout Shopcart with id [%s]", shopcart_id)

        # Attempt to find the Shopcart and abort if not found
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )
        shopcart.calculate_total_price()

        app.logger.info(
            "Checked out Shopcart with id [%s], total price is [%s]",
            shopcart_id,
            shopcart.total_price,
        )

        return {
            "id": shopcart.id,
            "total_price": float(shopcart.total_price),
        }, status.HTTP_200_OK


######################################################################
#  PATH: /shopcarts/{id}/items/{id}
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>")
@api.param("shopcart_id", "The Shopcart identifier")
@api.param("item_id", "The Shopcart Item identifier")
class ShopcartItemResource(Resource):
    """
    ShopcartItemResource class

    Allows the manipulation of a single Shopcart Item
    GET /shopcarts/{id}/items/{id} - Returns a Shopcart Item with the id
    PUT /shopcarts/{id}/items/{id} - Update a Shopcart Item with the id
    DELETE /shopcarts/{id}/items/{id} -  Deletes a Shopcart Item with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN ITEM FROM A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("get_shopcart_items")
    @api.response(404, "Shopcart Item not found")
    @api.marshal_with(shopcartItem_model)
    def get(self, shopcart_id, item_id):
        """
        Retrieve a single Item from Shopcart

        This endpoint will return a Item from Shopcart based on it's id
        """
        app.logger.info(
            "Request to Retrieve a Item with id [%s] from Shopcart with id [%s]",
            item_id,
            shopcart_id,
        )

        # Attempt to find the Shopcart and abort if not found
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )

        item = ShopcartItem.find(item_id)
        if not item or item.shopcart_id != shopcart_id:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id [{item_id}] was not found in Shopcart [{shopcart_id}].",
            )

        app.logger.info(
            "Returning Item with id [%s] in Shopcart with id [%s]",
            item_id,
            shopcart_id,
        )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE A SHOPCART ITEM
    # ------------------------------------------------------------------
    @api.doc("update_shopcart_items")
    @api.response(404, "Shopcart Item not found")
    @api.response(400, "The posted Shopcart Item data was not valid")
    @api.expect(shopcartItem_model)
    @api.marshal_with(shopcartItem_model)
    def put(self, shopcart_id, item_id):
        """
        Update an Item in a Shopcart

        This endpoint will update an Item in a Shopcart based on the body that is posted
        """
        app.logger.info(
            "Request to update Item with id [%s] in Shopcart with id [%s]",
            item_id,
            shopcart_id,
        )

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )

        app.logger.info("Processing: %s", api.payload)

        # Attempt to find the item and abort if not found
        item = ShopcartItem.find(item_id)
        if not item:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Item with id [{item_id}] was not found in Shopcart with id [{shopcart_id}].",
            )

        # Update the item with the new data
        item.deserialize(api.payload)

        # Save the updates to the database
        item.update()

        # update the total price of the shopcart
        shopcart.calculate_total_price()

        app.logger.info(
            "Item with id [%s] in Shopcart with id [%s] updated!",
            item_id,
            shopcart_id,
        )

        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A SHOPCART ITEM
    # ------------------------------------------------------------------
    @api.doc("delete_shopcart_items")
    @api.response(204, "Shopcart Item deleted")
    def delete(self, shopcart_id, item_id):
        """
        Delete an Item in a Shopcart

        This endpoint will delete an Item based on the id specified in the path
        """
        app.logger.info(
            "Request to delete Item with id [%s] in Shopcart with id [%s]",
            item_id,
            shopcart_id,
        )

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )

        # See if the item exists and delete it if it does
        item = ShopcartItem.find(item_id)
        if item:
            item.delete()
            shopcart.calculate_total_price()
            app.logger.info(
                "Item with id [%s] deleted from Shopcart with id [%s]!",
                item_id,
                shopcart_id,
            )

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /shopcarts/{id}/items
######################################################################
@api.route("/shopcarts/<int:shopcart_id>/items", strict_slashes=False)
@api.param("shopcart_id", "The Shopcart identifier")
class ShopcartItemCollection(Resource):
    """Handles all interactions with collections of Shopcart Items"""

    # ------------------------------------------------------------------
    # LIST ALL ITEMS IN A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("list_shopcart_items")
    @api.expect(shopcartItem_args, validate=True)
    @api.marshal_list_with(shopcartItem_model)
    def get(self, shopcart_id):
        """
        Retrieve all Items in a Shopcart
        """
        app.logger.info("Request to list Items in Shopcart with id [%s]", shopcart_id)

        # Attempt to find the Shopcart and abort if not found
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )

        # Get the query parameters
        args = shopcartItem_args.parse_args()
        product_id = args.get("product_id")
        name = args.get("name")

        items = shopcart.items
        if product_id:
            app.logger.info("Filtering by product ID [%s]", product_id)
            items = [item for item in items if item.product_id == product_id]
        if name:
            app.logger.info("Filtering by product name [%s]", name)
            items = [item for item in items if item.name == name]

        if not product_id and not name:
            app.logger.info("Returning unfiltered list.")

        items = [item.serialize() for item in items]

        app.logger.info(
            "Returning [%s] Items in Shopcart with id [%s]",
            len(items),
            shopcart_id,
        )

        return items, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD AN ITEM TO A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("create_shopcart_items")
    @api.response(400, "The posted Shopcart Item data was not valid")
    @api.expect(create_shopcartItem_model)
    @api.marshal_with(shopcartItem_model, code=201)
    def post(self, shopcart_id):
        """
        Add an Item in a Shopcart

        This endpoint will create an Item in a Shopcart based on the body that is posted
        """
        app.logger.info("Request to add an Item in Shopcart with id [%s]", shopcart_id)

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )

        data = api.payload

        app.logger.info("Processing: %s", data)

        item = ShopcartItem.find_by_product_id_shopcart_id(data["product_id"], shopcart_id)
        if item:
            # Update quantity if the item exists in the shopcart
            item.quantity += data["quantity"]
            item.update()
        else:
            # Add a new item if the item does not exist in the shopcart
            item = ShopcartItem()
            data["shopcart_id"] = shopcart_id
            item.deserialize(data)
            shopcart.items.append(item)
            shopcart.update()

        # update the total price of the shopcart
        shopcart.calculate_total_price()
        app.logger.info(
            "Item with id [%s] saved in Shopcart with id [%s]!", item.id, shopcart_id
        )

        # Return the location of the new item
        location_url = api.url_for(
            ShopcartItemResource,
            item_id=item.id,
            shopcart_id=shopcart_id,
            _external=True,
        )

        return item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # DELETE ALL ITEMS IN A SHOPCART
    # ------------------------------------------------------------------
    @api.doc("delete_all_shopcart_items")
    @api.response(204, "All Shopcart Items deleted")
    def delete(self, shopcart_id):
        """
        Delete all Items in a Shopcart

        This endpoint will delete all Items from a Shopcart based on the id specified in the path
        """
        app.logger.info(
            "Request to delete all Items in Shopcart with id [%s]",
            shopcart_id,
        )

        # See if the shopcart exists and abort if it doesn't
        shopcart = Shopcart.find(shopcart_id)
        if not shopcart:
            error(
                status.HTTP_404_NOT_FOUND,
                f"Shopcart with id [{shopcart_id}] was not found.",
            )

        for item in shopcart.items:
            item.delete()
        shopcart.calculate_total_price()

        app.logger.info("Items in Shopcart with id [%s] deleted!", shopcart_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


# ------------------------------------------------------------------
# Logs error messages before aborting
# ------------------------------------------------------------------
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    api.abort(status_code, reason)
