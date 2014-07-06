/*******************************************************************************
 * Simple script to submit forms
 * Copyright (c) 2013 Romain TOUZÉ
 ******************************************************************************/

/*jslint browser: true*/

var fieldsAreValid = function () {
    'use strict';
    console.debug('in fieldsAreValid');
    var username = document.getElementById('id_username'),
        email = document.getElementById('id_email'),
        password = document.getElementById('id_password'),
        password_check = document.getElementById('id_password_check'),
        invalidEmail = function () {
            var emailVal;
            if (email) {
                emailVal = email.value;
                return !emailVal.trim().toLowerCase().match(/^\w+@\w+\.[a-z]+$/);
            }
            return false;
        },

        invalidPassword = function () {
            return password.value.trim() === '' || password.value !== password_check.value;
        },

        showError = function (inputNode, message) {
            window.alert(message);
            inputNode.style.borderColor = 'red';
            inputNode.style.borderWidth = '3px';
        };

    if (username.value.trim() === '') {
        /* TODO attention, ce n'est pas internationnalisé...*/
        showError(username, 'Please enter a username.');
        return false;
    }

    if (invalidEmail()) {
        showError(email, 'Please enter a valid email.');
        return false;
    }

    if (invalidPassword()) {
        showError(password, 'Entered password is empty or not the same as your second entry.');
        return false;
    }
    return true;
};

$(function () {
    $('#submit_link').click(
        function (event) {
            'use strict';
            event.preventDefault();
            if (fieldsAreValid()) {
                console.debug('connard! tu valides ou quoi???');
                $('#signin_form').submit();
            }
        });
});
