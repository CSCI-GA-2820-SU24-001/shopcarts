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
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['id']}", timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new shopcarts
    for row in context.table:
        payload = {
            "id": row['id'],
            "total_price": row['total_price'],
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@given('the following shopcart items')
def step_impl(context):
    """ Delete all Shopcarts Items and load new ones """

    # Get a list all of the shopcarts
    rest_endpoint = f"{context.base_url}/shopcarts"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    assert context.resp.status_code == HTTP_200_OK
    # and delete all shopcart items in the shopcarts one by one
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['id']}/items", timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # Load the database with new shopcart items
    for row in context.table:
        payload = {
            "product_id": row["product_id"],
            "price": row["price"],
            "quantity": row["quantity"],
            "name": row["name"],
            "shopcart_id": row["customer_id"],
        }
        context.resp = requests.post(f"{rest_endpoint}/shopcarts/{row['id']}/items", json=payload, timeout=WAIT_TIMEOUT)
        assert context.resp.status_code == HTTP_201_CREATED
