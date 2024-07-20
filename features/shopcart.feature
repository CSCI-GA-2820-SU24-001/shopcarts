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

Scenario: List all Shopcarts
    When I visit the "Home Page"
    And I press the "Shopcart List" button
    Then I should see the message "Success"
    And I should see "Apple" in the "Shopcart" results
    And I should see "Orange" in the "Shopcart" results
    And I should see "Chocolate" in the "Shopcart" results
    And I should see "Bread" in the "Shopcart" results
    And I should not see "Random" in the "Shopcart" results

Scenario: Retrieve a Shopcarts
    When I visit the "Home Page"
    And I press the "Shopcart List" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I press the "Shopcart Form Clear" button
    And I paste the "Shopcart ID" field
    And I press the "Shopcart Retrieve" button
    Then I should see the message "Success"
    And I should see "2" in the "Shopcart total price" field

Scenario: Search for Shopcart by Product ID
    When I visit the "Home Page"
    And I set the "Shopcart Item Product ID" to "1"
    And I press the "Shopcart Search" button
    Then I should see the message "Success"
    And I should see "Apple" in the "Shopcart" results
    And I should not see "Orange" in the "Shopcart" results
    And I should not see "Chocolate" in the "Shopcart" results
    And I should not see "Bread" in the "Shopcart" results

Scenario: Search for Shopcart by Name
    When I visit the "Home Page"
    And I set the "Shopcart Item Name" to "Apple"
    And I press the "Shopcart Search" button
    Then I should see the message "Success"
    And I should see "Apple" in the "Shopcart" results
    And I should not see "Orange" in the "Shopcart" results
    And I should not see "Chocolate" in the "Shopcart" results
    And I should not see "Bread" in the "Shopcart" results

Scenario: Search for Shopcart by Name
    When I visit the "Home Page"
    And I set the "Shopcart Item Product ID" to "1"
    And I set the "Shopcart Item Name" to "Apple"
    And I press the "Shopcart Search" button
    Then I should see the message "Success"
    And I should see "Apple" in the "Shopcart" results
    And I should not see "Orange" in the "Shopcart" results
    And I should not see "Chocolate" in the "Shopcart" results
    And I should not see "Bread" in the "Shopcart" results