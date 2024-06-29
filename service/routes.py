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
and Delete Shopcarts
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Shopcart, ShopcartItem
from service.common import status  # HTTP Status Codes


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------
#                S H O P C A R T   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the Shopcarts"""
    app.logger.info("Request for shopcart list")

    shopcarts = []

    app.logger.info("Find all")
    shopcarts = Shopcart.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d shopcarts", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a single Shopcart

    This endpoint will return a Shopcart based on it's id
    """
    app.logger.info("Request to Retrieve a shopcart with id [%s]", shopcart_id)

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Creates a Shopcart

    This endpoint will create an Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to create an Shopcart")
    check_content_type("application/json")

    # Create the shopcart
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    shopcart.create()

    # Create a message to return
    message = shopcart.serialize()
    location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["PUT"])
def update_shopcarts(shopcart_id):
    """
    Update a Shopcart

    This endpoint will update an Shopcart based the body that is posted
    """
    app.logger.info("Request to update shopcart with id: %s", shopcart_id)
    check_content_type("application/json")

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    # Update from the json in the body of the request
    shopcart.deserialize(request.get_json())
    shopcart.id = shopcart_id
    shopcart.update()

    return jsonify(shopcart.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["DELETE"])
def delete_shopcart(shopcart_id):
    """
    Delete a Shopcart

    This endpoint will delete a Shopcart based on its id
    """
    app.logger.info("Request to delete shopcart with id: %s", shopcart_id)

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(shopcart_id)
    if shopcart:
        shopcart.delete()
    return "", status.HTTP_204_NO_CONTENT


# ---------------------------------------------------------------------
#            S H O P C A R T   I T E M   M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# LIST ALL ITEMS IN A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["GET"])
def list_shopcart_items(shopcart_id):
    """
    Retrieve all items in a Shopcart
    """
    app.logger.info("Request to list items in a shopcart with id [%s]", shopcart_id)

    # Attempt to find the Shopcart and abort if not found
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    items = [item.serialize() for item in shopcart.items]
    return jsonify(items), status.HTTP_200_OK


######################################################################
# RETRIEVE AN ITEM FROM A SHOPCART
######################################################################


######################################################################
# ADD AN ITEM TO A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["POST"])
def add_shopcart_items(shopcart_id):
    """
    Add an Item in a Shopcart

    This endpoint will create an Item in a Shopcart based the data in the body that is posted
    """
    app.logger.info("Request to Create an Item for Shopcart id: %s", (shopcart_id))
    check_content_type("application/json")
    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    data = request.get_json()
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
    app.logger.info("Item with new id [%s] saved!", item.id)

    # Prepare a message to return
    message = item.serialize()

    # todo - uncomment when "get_shopcart_items" is implemented
    # Return the location of the new item
    # location_url = url_for("get_shopcart_items", item_id=item.id, shopcart_id=shopcart_id, _external=True)
    location_url = "unknown"
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE A SHOPCART ITEM
######################################################################


######################################################################
# DELETE ALL ITEMS IN A SHOPCART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items", methods=["DELETE"])
def delete_all_shopcart_items(shopcart_id):
    """
    Delete all Items in a Shopcart

    This endpoint will delete all Items from a Shopcart based the id specified in the path
    """
    app.logger.info(
        "Request to delete all items for Shopcart id: %s",
        (shopcart_id),
    )

    # See if the shopcart exists and abort if it doesn't
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{shopcart_id}' was not found.",
        )

    for item in shopcart.items:
        item.delete()
    shopcart.calculate_total_price()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# DELETE A SHOPCART ITEM
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/items/<int:item_id>", methods=["DELETE"])
def delete_item(shopcart_id, item_id):
    """
    Delete an Item in Shopcart

    This endpoint will delete an Item based the id specified in the path
    """
    app.logger.info(
        "Request to delete Address %s for Account id: %s", (item_id, shopcart_id)
    )

    # See if the address exists and delete it if it does
    item = Shopcart.find(item_id)
    if item:
        item.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"No Content-Type specified, Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Invalid Content-Type {request.headers['Content-Type']}, Content-Type must be {content_type}",
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
