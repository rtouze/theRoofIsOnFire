from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'theRoofIsOnFire.views.home', name='home'),
    # url(r'^theRoofIsOnFire/', include('theRoofIsOnFire.foo.urls')),

    # Default view
    url(r'^$', 'theRoofIsOnFire.views.index', name='index'),

    url(r'^login$', 'theRoofIsOnFire.views.login', name='login'),
    url(r'^login/invalid/(?P<error_type>\w+)$',
        'theRoofIsOnFire.views.login_invalid',
        name='login'),

    url(r'^charts/', include('charts.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
