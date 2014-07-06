# -*- coding: utf-8 -*-
""" Common views for theRoofIsOnFire """
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import forms
from django.contrib.auth import authenticate, login as django_login
from django.utils.translation import ugettext as _

INVALID_LOGIN_MESSAGE = {
    'unknown': "Unknown user.",
    'invalid_data': "Error in entered data"
    " (did you fill all the fields?)" 
}

def index(request):
    """Redirect to the index page."""
    context = {'form': LoginForm() }
    return render(request, 'index.htm', context)

def login(request):
    """Process login information"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                username = form.cleaned_data['login']
                password = form.cleaned_data['password']
                user = authenticate(username=username, password=password)
                if user and user.is_active:
                    django_login(request, user)
                    return HttpResponseRedirect('/charts/dashboard/%d' % user.pk)
                else:
                    return HttpResponseRedirect('/login/invalid/unknown')
            except IndexError:
                return HttpResponseRedirect('/login/invalid/unknown')
        return HttpResponseRedirect('/login/invalid/invalid_data')
    # Back to index
    return HttpResponseRedirect('/')

def login_invalid(request, error_type): 
    """ Displays the index with an error message. """
    # TODO - encode authentification error message in URI
    try:
        message = INVALID_LOGIN_MESSAGE[error_type]
    except KeyError:
        message = "Erreur inconnue"

    context = {'form': LoginForm(), 'message': message }
    return render(request, 'index.htm', context)

class LoginForm(forms.Form):
    """Form used to enter login and password."""
    login = forms.CharField(label=_('Username:'), max_length=256)
    password = forms.CharField(label=_('Password:'), widget=forms.PasswordInput())
