Feature: The shopcart service back-end
    As a shopcart manager
    I need a RESTful catalog service
    So that I can keep track of all the shopcarts

Background:
    Given the following shopcarts
        | id    | total_price |
        | 1     | 1.0         |
        | 2     | 2.0         |
        | 3     | 3.0         |
    And the following shopcart items
        | product_id  | price   | quantity | name        | shopcart_id |
        | 1           | 1.0     | 2        | Apple       | 1           |
        | 2           | 1.0     | 4        | Orange      | 1           |
        | 3           | 3.0     | 3        | Chocolate   | 2           |
        | 4           | 2.5     | 1        | Bread       | 3           |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcarts RESTful Service" in the title
    And I should not see "404 Not Found"