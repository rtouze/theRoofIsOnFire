/*******************************************************************************
 * Helper script for create_project.htm page.
 * Copyright (c) 2013 Romain TOUZÉ
 ******************************************************************************/

var DATE_FORMAT="mm/dd/yy";

$(function (){
    $('#id_start_date').datepicker({ dateFormat: DATE_FORMAT });
    $('#id_end_date').datepicker({ dateFormat: DATE_FORMAT });
    /* TODO form validation */
    $('#submit_link').click(function () {
        $('#creation_form').submit();
    });
});

