var countItems = 0;
$(document).ready(function () { });

/** clicking on settings gear/login a tag in container */
$('#header #setting_gear').click(function () {
    console.log("here")
    $('.dropdown-menu').toggle();
})

$('.newCat_create_btn').click(function() {
    $('sport_name').prop('disabled', true)
})


/** clicking on settings gear logout button */
$('#AddItem').click(function () {
    $('.saveall_items').show()
    newChild = '<input type="text" name="sport_name" class="'+(countItems++)+'"'+'/><a href="javascript:void(0)" class="removeCatalogItem">X<br></a>';
    $('.items_form').append(newChild)
    // $.ajax({
    //     type: "get",
    //     url: '/gdisconnect',
    //     processData: false,
    //     contentType: 'application/octet-stream; charset=utf-8',
    //     success: function (result) {
    //         if (result) {
    //             login_session = null;
    //             document.cookie = "login_session=;expires=Thu, 01 Jan 1970 00:00:01 GMT;"
    //             userInfoShowHide(false)
    //         } else if (authResult['error']) {
    //             console.log("error")
    //         } else {
    //             $('#reuslt').html('failed .....')
    //         }
    //     }
    // })
})

$('.removeCatalogItem').click(function(){
    console.log($('.items_form'))
})

$('#create').click(function () {
    $.ajax({
        type: "post",
        url: '/catagories/new',
        processData: false,
        data: $('.sport_name').val(),
        contentType: 'application/octet-stream; charset=utf-8',
        success: function (result) {
            if (result) {
                $('#AddItem').show()
            } else {
                console.log("error")
            }
        }
    })
})

$('#SaveAll').click(function () {
    $.ajax({
        type: "post",
        url: '/catagories/new',
        processData: false,
        data: $('.sport_name').val(),
        contentType: 'application/octet-stream; charset=utf-8',
        success: function (result) {
            if (result) {
                $('#AddItem').show()
            } else {
                console.log("error")
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

