Feature: The shopcart service back-end
    As a shopcart manager
    I need a RESTful catalog service
    So that I can keep track of all the shopcarts and shopcart items

Background:
    Given the following shopcarts
        | total_price |
        | 0.0         |
        | 0.0         |
        | 0.0         |
        | 0.0         |
    And the following shopcart items
        | product_id  | price   | quantity | name        |
        | 1           | 1.0     | 2        | Apple       |
        | 2           | 1.0     | 4        | Orange      |
        | 3           | 3.0     | 3        | Chocolate   |
        | 4           | 2.5     | 1        | Bread       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcarts RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Shopcart
    When I visit the "Home Page"
    And I set the "Shopcart total price" to "10"
    And I press the "Shopcart Create" button
    Then I should see the message "Shopcart has been Created!"
    When I copy the "Shopcart ID" field
    And I press the "Shopcart Form Clear" button
    Then the "Shopcart ID" field should be empty
    And the "Shopcart Item product ID" field should be empty
    And the "Shopcart Item name" field should be empty
    And the "Shopcart total price" field should be empty
    When I paste the "Shopcart ID" field
    And I press the "Shopcart Retrieve" button
    Then I should see the message "Success"
    And I should see "10" in the "Shopcart total price" field