from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'BeerTasting.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'Beers.views.index', name='index'),
    
    url(r'^login/', 'Beers.views.login_view', name='login_view'),
    url(r'^login_failed/$', 'Beers.views.login_failed_view', name='login_failed_view'),
    url(r'^logout/', 'Beers.views.logout_view', name='logout_view'),
    url(r'^profile/$', 'Beers.views.profile_view', name='profile_view'),
    url(r'^beer/$', 'Beers.views.selected_beer', name='selected_beer'),
    url(r'^beer/(\d+)$', 'Beers.views.selected_beer', name='selected_beer'),
)
