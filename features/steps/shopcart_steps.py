# pylint: disable=function-redefined
# flake8: noqa
"""
Shopcart Steps

Steps file for Shopcart.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given('the following shopcarts')
def step_impl(context):
    """ Delete all Shopcarts and load new ones """

    # Get a list all of the shopcarts
    rest_endpoint = f"{context.base_url}/api/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['id']}", timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new shopcarts
    for row in context.table:
        payload = {
            "total_price": float(row['total_price'])
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given('the following shopcart items')
def step_impl(context):
    """ Delete all Shopcarts Items and load new ones """

    # Get a list all of the shopcarts
    rest_endpoint = f"{context.base_url}/api/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    assert context.resp.status_code == HTTP_200_OK
    # and delete all shopcart items in the shopcarts one by one
    shopcart_ids = []
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['id']}/items", timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)
        shopcart_ids.append(shopcart["id"])

    # Load the database with new shopcart items
    shopcart_index = 0  # Initialize index to assign shopcarts
    for row in context.table:
        shopcart_id = shopcart_ids[shopcart_index]  # Get the shopcart ID by index
        payload = {
            "product_id": int(row["product_id"]),
            "price": float(row["price"]),
            "quantity": int(row["quantity"]),
            "name": row["name"],
            "shopcart_id": shopcart_id,
        }
        context.resp = requests.post(f"{rest_endpoint}/{shopcart_id}/items", json=payload, timeout=WAIT_TIMEOUT)
        assert context.resp.status_code == HTTP_201_CREATED
        # Move to the next shopcart after assigning an items to the current shopcart
        shopcart_index = shopcart_index + 1
