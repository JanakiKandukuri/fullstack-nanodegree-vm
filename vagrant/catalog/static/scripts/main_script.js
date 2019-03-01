var main_banner = document.getElementById("main_banner");

$(document).ready(function () {
    if (document.cookie.includes('login_session')) {
        login_session = JSON.parse(document.cookie.split("=")[1])
        userInfoShowHide(true)
    } else {
        userInfoShowHide(false)
    }
    /** clicking on catalog a tag in container */
    $('.catalog').click(function () {
        var id = $(this).data("id");
        console.log(id);
        $("#items_types").html("")
        $.ajax({
            url: "/categories/" + id + "/item",
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

});

/** clicking on settings gear/login a tag in container */
$('#header #setting_gear').click(function () {
    console.log("here")
    $('.dropdown-menu').toggle();
})

function signInCallback(authResult) {
    if (authResult['code']) {
        var STATE = $('#signinButton').data('state');
        $('.dropdown-menu').toggle();
        $.ajax({
            type: "post",
            url: '/gconnect?state=' + STATE,
            processData: false,
            data: authResult['code'],
            contentType: 'application/octet-stream; charset=utf-8',
            success: function (result) {
                if (result) {
                    login_session = result['UserInfo'][0];
                    document.cookie = "login_session="+JSON.stringify(login_session);
                    userInfoShowHide(true);
                    window.location.href = "/user_catalog";
                    // $('#user_name').html(login_session['name'])
                } else if (authResult['error']) {
                    console.log("error")
                } else {
                    $('#reuslt').html('failed .....')
                }
            }
        })
    }
}

/** clicking on settings gear logout button */
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

/** show/ hide when user is logged in */
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
        $('.dropdown-menu').hide();
    }

}

