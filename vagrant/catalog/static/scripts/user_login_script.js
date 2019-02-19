$(document).ready(function () {
    $('#myList').addClass('active');
    $('#myList').click(function () {
        $('#myList').addClass('active');
        $('#allItems').removeClass('active');
        $('#all_list_table').hide();
        $('#user_list_table').show();
    })

    $('#allItems').click(function () {
        $('#allItems').addClass('active');
        $('#myList').removeClass('active');
        $('#all_list_table').show();
        $('#user_list_table').hide();
    });


    $('.delete_catalog').click(function () {

        var id = $(this).data("id");
        $.ajax({
            url: "/user_catalog/" + id + "/delete",
            type: "post",
            success: function (response) {
                window.location.href="user_catalog"

            },
            error: function (xhr) {
                console.log(xhr)
                //Do Something to handle error
            }
        });
    })

});