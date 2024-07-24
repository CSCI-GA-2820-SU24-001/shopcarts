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
    When I paste the "Shopcart Id" field
    And I press the "Shopcart Retrieve" button
    Then I should see the message "Success"
    And I should see "10" in the "Shopcart total price" field

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

Scenario: Update a Shopcart
    When I visit the "Home Page"
    And I set the "Shopcart Item Name" to "Apple"
    And I press the "Shopcart Search" button
    Then I should see the message "Success"
    And I should see "2" in the "Shopcart total price" field
    When I change "Shopcart total price" to "11.11"
    And I press the "Shopcart Update" button
    Then I should see the message "Shopcart has been Updated!"
    When I copy the "Shopcart ID" field
    And I press the "Shopcart Form Clear" button
    And I paste the "Shopcart ID" field
    And I press the "Shopcart Retrieve" button
    Then I should see the message "Success"
    And I should see "11.11" in the "Shopcart total price" field

Scenario: Delete a Shopcart
    When I visit the "Home Page"
    And I set the "Shopcart Item Name" to "Apple"
    And I press the "Shopcart Search" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I press the "Shopcart Form Clear" button
    And I paste the "Shopcart ID" field
    And I press the "Shopcart Delete" button
    Then I should see the message "Shopcart has been Deleted!"
    When I press the "Shopcart Form Clear" button
    And I paste the "Shopcart ID" field
    And I press the "Shopcart Retrieve" button
    Then I should not see "Success"

Scenario: Clear a Shopcart
    When I visit the "Home Page"
    And I set the "Shopcart Item Name" to "Apple"
    And I press the "Shopcart Search" button
    Then I should see the message "Success"
    When I copy the "Shopcart ID" field
    And I press the "Shopcart Form Clear" button
    And I paste the "Shopcart ID" field
    And I press the "Clear Cart" button
    Then I should see the message "Shopcart has been Cleared!"
    When I press the "Shopcart Form Clear" button
    And I paste the "Shopcart ID" field
    And I press the "Shopcart Retrieve" button
    Then I should see the message "Success"
    And I should see "0" in the "Shopcart total price" field

Scenario: List all Items in a Shopcart
    When I visit the "Home Page"
    And I press the "Shopcart List" button
    And I copy the "Shopcart ID" field
    And I paste the "Shopcart Item ID" field
    And I press the "Item List" button
    Then I should see the message "Success"
    And I should see "1" in the "Item" results
    And I should see "Apple" in the "Item" results
    And I should see "2" in the "Item" results
    And I should see "1" in the "Item" results
    And I should not see "Orange" in the "Item" results
    And I should not see "Chocolate" in the "Item" results
    And I should not see "Bread" in the "Item" results

Scenario: Create a Shopcart Item
    When I visit the "Home Page"
    And I press the "Shopcart List" button
    And I copy the "Shopcart ID" field
    And I paste the "Item Shopcart ID" field
    And I set the "Item Product ID" to "4"
    And I set the "Item Name" to "Cereal"
    And I set the "Item Quantity" to "1"
    And I set the "Item Price" to "6.5"
    And I press the "Item Create" button
    Then I should see the message "Shopcart Item has been Created!"
    When I copy the "Item Shopcart ID" and "Item ID" fields
    And I press the "Item Form Clear" button
    Then the "Item Shopcart ID" field should be empty
    And the "Item ID" field should be empty
    And the "Item Product ID" field should be empty
    And the "Item Name" field should be empty
    And the "Item Quantity" field should be empty
    And the "Item Price" field should be empty
    When I paste the "Shopcart Item ID" and "Item ID" fields
    # And I press the "Item Retrieve" button
    # Then I should see the message "Success"
    # And I should see "4" in the "Item Product ID" field
    # And I should see "Cereal" in the "Item Name" field
    # And I should see "1" in the "Item Quantity" field
    # And I should see "6.5" in the "Item Price" field