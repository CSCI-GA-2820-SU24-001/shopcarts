$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************


    // Updates the shopcart form with data from the response
    function update_shopcart_form_data(res) {
        $("#shopcart_id").val(res.id);
        $("#shopcart_total_price").val(res.total_price);
        $("#shopcart_item_product_id").val(res.item_product_id);
        $("#shopcart_item_name").val(res.item_name);
    }

    // Updates the shopcart item form with data from the response
    function update_shopcart_item_form_data(res) {
        $("#item_id").val(res.id);
        $("#item_shopcart_id").val(res.shopcart_id);
        $("#item_product_id").val(res.product_id);
        $("#item_name").val(res.name);
        $("#item_price").val(res.price);
        $("#item_quantity").val(res.quantity);
    }

    // Clears all shopcart form fields
    function clear_shopcart_form_data() {
        $("#shopcart_id").val("");
        $("#shopcart_total_price").val("");
        $("#shopcart_item_product_id").val("");
        $("#shopcart_item_name").val("");
    }

    // Clears all shopcart item form fields
    function clear_shopcart_item_form_data() {
        $("#item_id").val("");
        $('#shopcart_item_id').val("");
        $("#item_shopcart_id").val("");
        $("#item_product_id").val("");
        $("#item_name").val("");
        $("#item_price").val("");
        $("#item_quantity").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }


    // ****************************************
    //  S H O P C A R T   F U N C T I O N S
    // ****************************************


    // ****************************************
    // Create a Shopcart
    // ****************************************



    // ****************************************
    // Retrieve a Shopcart
    // ****************************************



    // ****************************************
    // Update a Shopcart
    // ****************************************



    // ****************************************
    // Delete a Shopcart
    // ****************************************



    // ****************************************
    // List Shopcarts
    // ****************************************



    // ****************************************
    // Search Shopcarts
    // ****************************************



    // ****************************************
    // Clear a Shopcart
    // ****************************************



    // ****************************************
    // Checkout a Shopcart
    // ****************************************



    // ****************************************
    // Clear the Shopcart form
    // ****************************************

    $("#shopcart-form-clear-btn").click(function () {
        $("#flash_message").empty();
        clear_shopcart_form_data()
    });


    // **************************************************
    //  S H O P C A R T   I T E M   F U N C T I O N S
    // **************************************************


    // ****************************************
    // Create a Shopcart Item
    // ****************************************



    // ****************************************
    // Retrieve a Shopcart Item
    // ****************************************



    // ****************************************
    // Update a Shopcart Item
    // ****************************************



    // ****************************************
    // Delete a Shopcart Item
    // ****************************************



    // ****************************************
    // List Shopcart Items
    // ****************************************



    // ****************************************
    // Clear the Shopcart Item form
    // ****************************************

    $("#item-form-clear-btn").click(function () {
        $("#flash_message").empty();
        clear_shopcart_item_form_data()
    });

})
