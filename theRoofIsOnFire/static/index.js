/******************************************************************************
 * Script for theRoofIsOnFire. Control the index page. Needs JQuery 2
 *****************************************************************************/

// TODO put eh login frame in a JQueryUI Dialog... Why not...

$(function () {
    $('#please_log_me_in').click(function () {
        $('#login_frame').show();
    });
    $('#close_button').click(function () {
        $('#login_frame').hide();
    });
    $('#login_submit_button').click(function () {
        $('#login_form').submit();
    })
});
