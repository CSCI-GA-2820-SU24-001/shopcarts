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

    $("#shopcart-create-btn").click(function () {
        let total_price = $("#shopcart_total_price").val();

        let data = {
            "total_price": parseFloat(total_price)
        };

        $("#shopcart_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_shopcart_form_data(res)
            flash_message("Shopcart has been Created!")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

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

    $("#shopcart-list-btn").click(function () {
        $("#shopcart_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function (res) {
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Shopcart ID</th>'
            table += '<th class="col-md-1">Total Price</th>'
            table += '<th class="col-md-1">Item ID</th>'
            table += '<th class="col-md-2">Item Product ID</th>'
            table += '<th class="col-md-2">Item Name</th>'
            table += '<th class="col-md-2">Item Quantity</th>'
            table += '<th class="col-md-2">Item Price</th>'
            table += '</tr></thead><tbody>'

            let firstShopcart = "";
            for (let i = 0; i < res.length; i++) {
                let shopcart = res[i];
                let items = shopcart['items'];
                let rowspan = items.length || 1;

                table += `<tr><td rowspan="${rowspan}">${shopcart.id}</td><td rowspan="${rowspan}">${shopcart.total_price}</td>`;

                if (items.length != 0) {
                    table += `<td>${items[0]['id']}</td><td>${items[0]['product_id']}</td><td>${items[0]['name']}</td><td>${items[0]['quantity']}</td><td>${items[0]['price']}</td></tr>`;
                    for (let j = 1; j < items.length; j++) {
                        table += `<tr><td>${items[j]['id']}</td><td>${items[j]['product_id']}</td><td>${items[j]['name']}</td><td>${items[j]['quantity']}</td><td>${items[j]['price']}</td></tr>`;
                    }
                } else {
                    table += `<td colspan="4"></td></tr>`;
                }

                if (i == 0) {
                    firstShopcart = shopcart;
                }
            }
            table += '</tbody></table>';
            $("#shopcart_search_results").append(table);

            // Copy the first result to the form
            if (firstShopcart != "") {
                update_shopcart_form_data(firstShopcart)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Search Shopcarts
    // ****************************************
    
    $("#shopcart-search-btn").click(function () {
        let item_product_id = $("#shopcart_item_product_id").val();
        let item_name = $("#shopcart_item_name").val();

        $("#shopcart_search_results").empty();
        $("#flash_message").empty();

        if (!item_product_id && !item_name) {
            flash_message("Please enter a search query.");
            return;
        }

        let queryString = "";
        if (item_product_id) {
            queryString += 'product_id=' + item_product_id + '&';
        }
        if (item_name) {
            queryString += 'name=' + item_name;
        }

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts?${queryString}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function (res) {
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Shopcart ID</th>'
            table += '<th class="col-md-1">Total Price</th>'
            table += '<th class="col-md-1">Item ID</th>'
            table += '<th class="col-md-2">Item Product ID</th>'
            table += '<th class="col-md-2">Item Name</th>'
            table += '<th class="col-md-2">Item Quantity</th>'
            table += '<th class="col-md-2">Item Price</th>'
            table += '</tr></thead><tbody>'

            let firstShopcart = "";
            for (let i = 0; i < res.length; i++) {
                let shopcart = res[i];
                let items = shopcart['items'];
                let rowspan = items.length || 1;

                table += `<tr><td rowspan="${rowspan}">${shopcart.id}</td><td rowspan="${rowspan}">${shopcart.total_price}</td>`;

                if (items.length != 0) {
                    table += `<td>${items[0]['id']}</td><td>${items[0]['product_id']}</td><td>${items[0]['name']}</td><td>${items[0]['quantity']}</td><td>${items[0]['price']}</td></tr>`;
                    for (let j = 1; j < items.length; j++) {
                        table += `<tr><td>${items[j]['id']}</td><td>${items[j]['product_id']}</td><td>${items[j]['name']}</td><td>${items[j]['quantity']}</td><td>${items[j]['price']}</td></tr>`;
                    }
                } else {
                    table += `<td colspan="4"></td></tr>`;
                }

                if (i == 0) {
                    firstShopcart = shopcart;
                }
            }
            table += '</tbody></table>';
            $("#shopcart_search_results").append(table);

            // Copy the first result to the form
            if (firstShopcart != "") {
                update_shopcart_form_data(firstShopcart)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


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
