/** clicking on settings gear/login a tag in container */
$('#header #setting_gear').click(function () {
    $('.dropdown-menu').toggle();
})


/** ********************** ON CREATE DISABLE TEXT FIELD AND ENABLE BUTTONS **************** */
$('.newCat_create_btn').click(function () {
    $('sport_name').prop('disabled', true)
})


/** ********************** ON ADD BUTTON CLICK ENABLE SAVEALL AND FORM FOR EQUIPMENTS **************** */
$('.newCat_Add_btn').click(function () {
    $('.saveall_items').show()
    newChild = '<div class="sport_item"><label class="input_label">Equipment Name:</label><input type="text" name="equipment_name" class="equipment_name ml-10" /><label class="input_label ml-10">Description:</label><input type="text" name="description" class="description ml-10" /><a href="javascript:void(0)" class="removeCatalogItem">X<br></a></div>'
    $('.items_form').append(newChild)
})


/** ********************** ON REMOVE CLICK REMOVE SPECIFIED ROW **************** */
$(document).on("click",".removeCatalogItem",function(){
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


