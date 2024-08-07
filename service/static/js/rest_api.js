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
            url: "/api/shopcarts",
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
    $("#shopcart-retrieve-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();

        $("#shopcart_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: ''
        })

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

            let shopcart = res;
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

            table += '</tbody></table>';
            $("#shopcart_search_results").append(table);

            update_shopcart_form_data(shopcart);
            flash_message("Success");
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Update a Shopcart
    // ****************************************
    $("#shopcart-update-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();
        let total_price = $("#shopcart_total_price").val();

        let data = {
            "total_price": parseFloat(total_price)
        };

        $("#shopcart_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_shopcart_form_data(res)
            flash_message("Shopcart has been Updated!")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Delete a Shopcart
    // ****************************************
    $("#shopcart-delete-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();

        $("#shopcart_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_shopcart_form_data()
            flash_message("Shopcart has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });


    // ****************************************
    // List Shopcarts
    // ****************************************
    $("#shopcart-list-btn").click(function () {
        $("#shopcart_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts`,
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

        let queryString = "";
        if (item_product_id) {
            queryString += 'product_id=' + item_product_id + '&';
        }
        if (item_name) {
            queryString += 'name=' + item_name;
        }

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts?${queryString}`,
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
    $("#clear-cart-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();
        $("#shopcart_search_results").empty();
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: '',
        })
        ajax.done(function (res) {
            clear_shopcart_form_data()
            flash_message("Shopcart has been Cleared!")
        });
        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });


    // ****************************************
    // Checkout a Shopcart
    // ****************************************
    $("#checkout-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();

        $("#shopcart_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${shopcart_id}/checkout`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">Shopcart ID</th>'
            table += '<th class="col-md-2">Total Price</th>'
            table += '</tr></thead><tbody>'

            let shopcart = res;
            table += `<tr><td>${shopcart.id}</td><td>${shopcart.total_price}</td></tr>`;
            table += '</tbody></table>';
            $("#shopcart_search_results").append(table);

            update_shopcart_form_data(shopcart);
            flash_message("Shopcart has been Checked Out!");
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });
    });


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
    $("#item-create-btn").click(function () {
        let shopcart_id = $("#item_shopcart_id").val();
        let product_id = $("#item_product_id").val();
        let name = $("#item_name").val();
        let price = $("#item_price").val();
        let quantity = $("#item_quantity").val();

        let data = {
            "shopcart_id": parseInt(shopcart_id),
            "product_id": parseInt(product_id),
            "name": name,
            "price": parseFloat(price),
            "quantity": parseInt(quantity)
        };

        $("#item_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: `/api/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_shopcart_item_form_data(res)
            flash_message("Shopcart Item has been Created!")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Retrieve a Shopcart Item
    // ****************************************
    $("#item-retrieve-btn").click(function () {
        let shopcart_id = $("#shopcart_item_id").val();
        let item_id = $("#item_id").val();

        $("#item_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">Item ID</th>';
            table += '<th class="col-md-2">Shopcart ID</th>';
            table += '<th class="col-md-2">Item Product ID</th>';
            table += '<th class="col-md-2">Item Name</th>';
            table += '<th class="col-md-2">Item Quantity</th>';
            table += '<th class="col-md-2">Item Price</th>';
            table += '</tr></thead><tbody>';

            let item = res;
            table += `<tr><td>${item['id']}</td><td>${item['shopcart_id']}</td><td>${item['product_id']}</td><td>${item['name']}</td><td>${item['quantity']}</td><td>${item['price']}</td></tr>`;

            table += '</tbody></table>';
            $("#item_search_results").append(table);

            update_shopcart_item_form_data(item);
            flash_message("Success");
        });

        ajax.fail(function (res) {
            clear_shopcart_item_form_data()
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Update a Shopcart Item
    // ****************************************
    $("#item-update-btn").click(function () {
        let shopcart_id = $("#shopcart_item_id").val();
        let item_id = $("#item_id").val();
        let product_id = $("#item_product_id").val();
        let name = $("#item_name").val();
        let price = $("#item_price").val();
        let quantity = $("#item_quantity").val();

        let data = {
            "shopcart_id": parseInt(shopcart_id),
            "product_id": parseInt(product_id),
            "name": name,
            "price": parseFloat(price),
            "quantity": parseInt(quantity)
        };

        $("#item_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_shopcart_item_form_data(res)
            flash_message("Shopcart Item has been Updated!")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Delete a Shopcart Item
    // ****************************************
    $("#item-delete-btn").click(function () {
        let shopcart_id = $("#shopcart_item_id").val();
        let item_id = $("#item_id").val();

        $("#item_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/shopcarts/${shopcart_id}/items/${item_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_shopcart_item_form_data()
            flash_message("Shopcart Item has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });


    // ****************************************
    // List Shopcart Items
    // ****************************************
    $("#item-list-btn").click(function () {
        let shopcart_id = $("#shopcart_item_id").val();

        $("#item_search_results").empty();
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function (res) {
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">Item ID</th>';
            table += '<th class="col-md-2">Shopcart ID</th>';
            table += '<th class="col-md-2">Item Product ID</th>';
            table += '<th class="col-md-2">Item Name</th>';
            table += '<th class="col-md-2">Item Quantity</th>';
            table += '<th class="col-md-2">Item Price</th>';
            table += '</tr></thead><tbody>';

            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr><td>${item['id']}</td><td>${item['shopcart_id']}</td><td>${item['product_id']}</td><td>${item['name']}</td><td>${item['quantity']}</td><td>${item['price']}</td></tr>`;

                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#item_search_results").append(table);

            if (firstItem != "") {
                update_shopcart_item_form_data(firstItem);
            }

            flash_message("Success");
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Search Shopcart Items
    // ****************************************
    $("#item-search-btn").click(function () {
        let shopcart_id = $("#shopcart_item_id").val();
        let product_id = $("#item_product_id").val();
        let name = $("#item_name").val();

        $("#item_search_results").empty();
        $("#flash_message").empty();

        let queryString = "";
        if (product_id) {
            queryString += 'product_id=' + product_id + '&';
        }
        if (name) {
            queryString += 'name=' + name;
        }

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${shopcart_id}/items?${queryString}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function (res) {
            let table = '<table class="table table-striped" cellpadding="10">';
            table += '<thead><tr>';
            table += '<th class="col-md-2">Item ID</th>';
            table += '<th class="col-md-2">Shopcart ID</th>';
            table += '<th class="col-md-2">Item Product ID</th>';
            table += '<th class="col-md-2">Item Name</th>';
            table += '<th class="col-md-2">Item Quantity</th>';
            table += '<th class="col-md-2">Item Price</th>';
            table += '</tr></thead><tbody>';

            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr><td>${item['id']}</td><td>${item['shopcart_id']}</td><td>${item['product_id']}</td><td>${item['name']}</td><td>${item['quantity']}</td><td>${item['price']}</td></tr>`;

                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#item_search_results").append(table);

            if (firstItem != "") {
                update_shopcart_item_form_data(firstItem);
            }

            flash_message("Success");
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    
    // ****************************************
    // Clear the Shopcart Item form
    // ****************************************
    $("#item-form-clear-btn").click(function () {
        $("#flash_message").empty();
        clear_shopcart_item_form_data()
    });

})
