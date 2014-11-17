#-*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from datetime import date
import json
import re

from charts.models import ChartProject, Task

def index(request):
    context = {}
    return render(request, 'index.htm', context)

def signin(request):
    context = { 'form': UserForm() }
    return render(request, 'signin.htm', context)

def valid_signin(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                        username = form.cleaned_data['username'],
                        first_name = form.cleaned_data['first_name'],
                        last_name = form.cleaned_data['last_name'],
                        email = form.cleaned_data['email'],
                        password = form.cleaned_data['password'],
                        )
                return HttpResponseRedirect('/charts/dashboard/%d' % user.pk)
            except IntegrityError:
                context = {
                    'error_message': 'Username {0} already exists.'.format(
                        form.cleaned_data['username']
                    ),
                    'form': form
                }
                return render(request, 'signin.htm', context)
        else:
            print("il est pas valide")
    return HttpResponseRedirect('/')

@login_required(login_url='/login/invalid/unknown')
def dashboard(request, user_id):
    # josh, user de test.
    user = User.objects.get(pk=user_id)
    user_projects = []
    user_projects = ChartProject.objects.filter(admin=user)
    context = {'user': user, 'user_projects': user_projects}
    #return HttpResponseRedirect('')
    return render(request, 'dashboard.htm', context)

@login_required(login_url='/login/invalid/unknown')
def project(request, user_id, project_id):
    project = ChartProject.objects.get(pk=project_id)
    tasks = Task.objects.filter(project = project)
    context = {'project': project, 'tasks': tasks, 'user_id': user_id}
    return render(request, 'project.htm', context)

@login_required(login_url='/login/invalid/unknown')
def new_project(request, user_id):
    user = User.objects.get(pk=user_id)
    action_url = '/charts/project/new/%d' % user.id
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # TODO: what if the form is invalid?
            project = ChartProject(name = form.cleaned_data['name'])
            project.start_date = form.cleaned_data['start_date']
            project.end_date = form.cleaned_data['end_date']
            project.admin = user
            project.save()
            return HttpResponseRedirect('/charts/dashboard/%s' % user_id)
    else:
        form = ProjectForm()

    context = {'user': user, 'form': form, 'action_url': action_url}
    return render(request, 'create_project.htm', context)

@login_required(login_url='/login/invalid/unknown')
def edit_project(request, user_id, project_id):
    """Method called to edit a project. If called with post method, the project
    is modified in the database. If called with another method, the project
    edit form is rendered."""
    user = User.objects.get(pk=user_id)
    project = ChartProject.objects.get(pk=project_id)
    action_url = '/charts/project/edit/%d/%d' % (user.id, project.id)
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project.name = form.cleaned_data['name']
            project.start_date = form.cleaned_data['start_date']
            project.end_date = form.cleaned_data['end_date']
            project.save()
            return HttpResponseRedirect('/charts/dashboard/%s' % user_id)
        return HttpResponseRedirect('/charts/dashboard/%s' % user_id)

    data = {'name': project.name,
            'start_date': project.start_date,
            'end_date': project.end_date
            }
    form = ProjectForm(data)
    context = {'user': user, 'form': form, 'action_url': action_url}
    return render(request, 'create_project.htm', context)

@login_required(login_url='/login/invalid/unknown')
def remove_project(request, user_id, project_id):
    # TODO Post a message to tel the project is deleted
    # TODO Put the project in a recycle bin rather than destroying it
    p = ChartProject.objects.get(pk=project_id)
    p.delete() # VIOLENCE
    return HttpResponseRedirect('/charts/dashboard/%s' % user_id)

def update_project_tasks(request, project_id):
    if request.method == 'POST':
        project = ChartProject.objects.get(pk=project_id)
        for t in Task.objects.filter(project=project):
            t.delete()

        sentTasks = json.loads(request.body)
        for sTask in sentTasks:
            t = Task()
            t.task_name = sTask['task_name']
            t.points = sTask['points']
            t.project = project
            try:
                temp_date = [int(i) for i in sTask['end_date'].split('/')]
                t.end_date = date(temp_date[2], temp_date[0], temp_date[1])
            except ValueError:
                # TODO - use Django logger
                print('ERROR - Wrong date format for %s.' % sTask['end_date'])
            t.save()
    return HttpResponse()

@login_required(login_url='/login/invalid/unknown')
def edit_user(request, user_id):
    user = User.objects.get(pk=user_id)
    if  request.method == 'POST':
        form = UserModificationForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            return HttpResponseRedirect('/charts/dashboard/{0}'.format(user_id))

    data = {
        'first_name': user.first_name,
        'last_name': user.last_name
    }
    form = UserModificationForm(data)
    context = {'form': form, 'user': user}
    return render(request, 'edit_user.htm', context)

class ProjectForm(forms.Form):
    name = forms.CharField(label=_('Project name'), max_length=256)
    date_formats = ['%m/%d/%Y', "%Y-%m-%d"]
    # TODO: localize date display
    start_date = forms.DateField(
        label=_('Project start date:'),
        input_formats=date_formats
    )
    # TODO: the style is not wide enough
    end_date = forms.DateField(
        label=_('Est. project end end'),
        input_formats=date_formats
    )

# TODO : pretty sure it's not the right way to do, but I'll learn from my mistakes
class UserForm(forms.Form):
    """
    Form displayed on signin page to allow a user to create an account.
    """
    username = forms.CharField(label=_('Username:'), max_length=256)
    first_name = forms.CharField(label=_('Firstname:'),
                                 max_length=256,
                                 required=False)

    last_name = forms.CharField(label=_('Lastname:'),
                                max_length=256,
                                required=False)

    email = forms.EmailField(label=_('Email:'), max_length=256)

    password = forms.CharField(label=_('Password:'),
                               max_length=256,
                               widget=forms.PasswordInput())

    password_check = forms.CharField(label=_('Check your password:'),
                                     max_length=256,
                                     widget=forms.PasswordInput())


    def is_valid(self):
        """Overrides is_valid to check if password and password_check are
        equals. Notice that the test should normally be handled on client side
        first."""
        super(UserForm, self).is_valid()
        if self.cleaned_data['password'] != self.cleaned_data['password_check']:
            return False;
        return True

    # TODO : presence / absence validation test ?
    #phone = forms.CharField(label=u'Téléphone :', max_length=256)

class UserModificationForm(forms.Form):
    '''Form for user modification page. Present limited field for modification'''
    first_name = forms.CharField(label=_('Firstname:'),
                                 max_length=256,
                                 required=False)

    last_name = forms.CharField(label=_('Lastname:'),
                                max_length=256,
                                required=False)
