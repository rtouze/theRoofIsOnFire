from django.conf.urls import patterns, url
from charts import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^signin$', views.signin, name='signin'),
    url(r'^valid_signin$', views.valid_signin, name='valid_signin'),
    url(r'^dashboard/(?P<user_id>\d+)$', views.dashboard, name='dashboard'),
    url(r'^project/(?P<user_id>\d+)/(?P<project_id>\d+)$',
        views.project,
        name='project'),

    url(r'^project/new/(?P<user_id>\d+)$', views.new_project, name='new_project'),

    url(r'^project/edit/(?P<user_id>\d+)/(?P<project_id>\d+)$',
        views.edit_project,
        name='edit_project'),

    url(r'^project/remove/(?P<user_id>\d+)/(?P<project_id>\d+)$',
        views.remove_project,
        name='remove_project'),

    url(r'^update_tasks/(?P<project_id>\d+)',
       views.update_project_tasks,
       name='update_project_tasks'),

    url(r'^user/edit/(?P<user_id>\d+)',
       views.edit_user,
       name='edit_user')
)

