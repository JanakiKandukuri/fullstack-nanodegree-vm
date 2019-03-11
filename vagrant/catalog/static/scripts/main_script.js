 /** HELPER FUNCTIONS */
 function userInfoShowHide(show) {
    if (show) {
        $('.user_info').show();
        $('#signOutButton').show();
        $('#signinButton').hide();
        $('.user_name').html(login_session['name']);
        $('.create_new').show();
        if (login_session['picture']) {
            $('.avatar').show();
            $('#avatar_img').attr('src', login_session['picture']);
        }
    } else {
        $('.user_info').hide();
        $('#signOutButton').hide();
        $('.avatar').hide();
        $('#signinButton').show();
        $('.create_new').hide();
        $('#settings_menu').hide();
    }

}

var user_id;


$(document).ready(function () {
    /** **DOCUMENT READY ACTIONS ** */
    $('#myList').addClass('active');
    if(document.cookie.includes('login_session')) {
        var cookieLogin = document.cookie.split(";")[2];
        var login_session = (JSON.parse(cookieLogin.split("=")[1]))
        $('.user_info').show();
        $('#signOutButton').show();
        $('#signinButton').hide();
        $('.user_name').html(login_session['name']);
        $('.create_new').show();
        if (login_session['picture']) {
            $('.avatar').show();
            $('#avatar_img').attr('src', login_session['picture']);
        }
    } else {
        $('.user_info').hide();
        $('#signOutButton').hide();
        $('.avatar').hide();
        $('#signinButton').show();
        $('.create_new').hide();
        $('#settings_menu').hide();
    }
});


   

/** **METHOD: SIGNIN BUTTON CLICK
   * **DESC: IN CATALOG MAIN PAGE, CLICK SIGNIN BTN TO LOGIN AS USER */
$('#signinButton').click(function () {
    function signInCallback(authResult) {
        var STATE = $('#signinButton').data('state')
        if (authResult['code']) {
            $('.dropdown-menu').toggle();
            $.ajax({
                type: 'POST',
                url: '/gconnect?state=' + STATE,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                contentType: 'application/octet-stream; charset=utf-8',
                success: function (result) {
                    login_session = result['UserInfo'][0];
                    this.user_id = login_session['id']
                    document.cookie = "login_session=" + JSON.stringify(login_session);
                    window.location.href = '/categories/user/'+login_session['id']
                    userInfoShowHide(true);
                    
                },
                processData: false,
                data: authResult['code']
            });
        } else {
            // handle error
            console.log('There was an error: ' + authResult['error']);
            $('#result').html('Failed to make a server-side call. Check your configuration and console.');
        }
    }
    auth2.grantOfflineAccess().then(signInCallback);
});

/** **METHOD: SIGNOUT BUTTON CLICK
   * **DESC: IN USERS PAGES, CLICK SIGNOUT BTN TO NAVIGATE TO MAIN PAGE */
$('#signOut').click(function () {
    $.ajax({
        type: "get",
        url: '/gdisconnect',
        processData: false,
        contentType: 'application/octet-stream; charset=utf-8',
        success: function (result) {
            if (result) {
                login_session = null;
                document.cookie = "login_session=;expires=Thu, 01 Jan 1970 00:00:01 GMT;"
                userInfoShowHide(false)
            } else if (authResult['error']) {
                console.log("error")
            } else {
                $('#reuslt').html('failed .....')
            }
        }
    })
})


/** **METHOD: MYLIST BUTTON CLICK
   * **DESC: IN USERS MAIN PAGE, CLICK MYLIST BTN TO VIEW USERS LIST OF CATALOG */
$('#myList').click(function () {
    $('#myList').addClass('active');
    $('#allItems').removeClass('active');
    $('#all_list_table').hide();
    $('#user_list_table').show();
    $('.create_new_btn').show();
})

/** **METHOD: TOOGLE SETTINGS DROPDOWN TO LOGIN */
$('#setting_gear').on('click', function () {
    $('.dropdown-menu').toggle();
})

/** **METHOD: ALLITEMS BUTTON CLICK
 * **DESC: IN USERS MAIN PAGE, CLICK ALLITEMS BTN TO VIEW ALL CATALOG */
$('#allItems').click(function () {
    $('#allItems').addClass('active');
    $('#myList').removeClass('active');
    $('#all_list_table').show();
    $('#user_list_table').hide();
    $('.create_new_btn').hide();
});


/** **METHOD: DELETE CATALOG BUTTON CLICK
 * **DESC: IN USERS MAIN PAGE, CLICK DELTE OR 'X' BTN TO DELETE AN ENTRY FROM LIST OF CATALOG */
$('.delete_catalog').click(function () { 
    var id = $(this).data("id");
    var name = $(this).data("name");
    var user_id = $(this).data("user_id");
    $('.modal-body').html("Are you sure to delete catalog "+(name));
    $('.save').click(function(){
        $.ajax({
            url: "/categories/user/" + user_id + "/category/"+ id+"/delete",
            type: "post",
            success: function (response) {
                window.location.href = "/categories/user/"+user_id;
    
            },
            error: function (xhr) {
                console.log(xhr)
            }
        });
    });
})

/** **METHOD: EDIT BUTTON CLICK
 * **DESC: IN USERS MAIN PAGE, CLICK EDIT BTN TO VIEW EDIT AN ENTRY FROM CATALOG */
$('.edit_catalog').click(function () {
    var id = $(this).data("id");
    $.ajax({
        url: "/user_catalog/" + id + "/edit",
        type: "get",
        success: function (response) {
            console.log(response)
        },
        error: function (xhr) {
            console.log(xhr)
        }
    });
})

/** clicking on catalog a tag in container */
$('.catalog').click(function () {
    var id = $(this).data("id");
    console.log(id);
    $("#items_types").html("")
    $.ajax({
        url: "/categories/" + id,
        type: "get",
        success: function (response) {
            console.log(response)
            var str = "<ul>";
            for (var i = 0; i < response.CatalogItem.length; i++) {
                str += "<li><a href='javascript:void(0)' data-item_id=" + response.CatalogItem[i].id + " data-id=" + id +
                    " class='item'>" + response.CatalogItem[i].name +
                    "</a>" + "<div>" + response.CatalogItem[i].description + "</div>"
            }
            str += "</ul>";
            $("#cat_items").html(str);
        },
        error: function (xhr) {
            console.log(xhr)
            //Do Something to handle error
        }
    });
});

/** clicking on sub item a tag in container */
$(document).on('click', 'a.item', function () {
    var id = $(this).data("id");
    var item_id = $(this).data("item_id");
    console.log(id);
    $.ajax({
        url: "/categories/" + id + "/" + item_id + "/type",
        type: "get",
        success: function (response) {
            console.log(response)
            var str = "<ul>";
            for (var i = 0; i < response.CatalogItemType.length; i++) {
                str += "<li><div >" + response.CatalogItemType[i].name +
                    "</div>" + "<div > " + response.CatalogItemType[i].description + "</div>"
            }
            str += "</ul>";
            $("#items_types").html(str);
        },
        error: function (xhr) {
            console.log(xhr)
        }
    });
});


/** ********************** ON CREATE DISABLE TEXT FIELD AND ENABLE BUTTONS **************** */
$('.newCat_create_btn').click(function () {
    $('sport_name').prop('disabled', true)
})


/** ********************** ON ADD BUTTON CLICK ENABLE SAVEALL AND FORM FOR EQUIPMENTS **************** */
$('.newCat_Add_btn').click(function () {
    $('.saveall_items').show()
    newChild = '<div class="sport_item"><label class="input_label">Equipment Name:</label><input type="text" name="equipment_name" class="equipment_name ml-10" /><label class="input_label ml-17">Description:</label><textarea name="description" rows="2" cols="20" class="description ml-10" value="{{c.description}}"></textarea><a href="javascript:void(0)" class="removeCatalogItem">X<br></a></div>'
    $('.items_form').append(newChild)
})


/** ********************** ON REMOVE CLICK REMOVE SPECIFIED ROW **************** */
$(document).on("click", ".removeCatalogItem", function () {
    $(this).parent().remove()
});

/** ********************** ON SAVE ALL SAVE ALL EQUIPMENTS AND NAVIGATE TO USER HOME PAGE **************** */
$('.newCat_saveall_items').click(function () {
    var id = $('.sport_name').data("id");
    var equipment_names = [];
    var descriptions = [];
    var items = [];
    $('.equipment_name').each(function () {
        equipment_names.push(($(this).val()));
    });
    $('.description').each(function () {
        descriptions.push(($(this).val()));
    });
    for (var i = 0; i < equipment_names.length; i++) {
        items.push([equipment_names[i], descriptions[i]])
    }
    console.log(items)
    $.ajax({
        type: "post",
        url: '/user_catalog/' + id + '/newItem',
        processData: false,
        data: JSON.stringify(items),
        contentType: 'application/octet-stream; charset=utf-8',
        success: function (result) {
            if (result) {
                window.location.href = result
            } else {
                $('#reuslt').html('failed .....')
            }
        }
    })
});




