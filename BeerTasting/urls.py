from django.conf.urls import patterns, include, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'BeerTasting.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^$', 'Beers.views.index', name='index'),

    url(r'^beers/', 'Beers.views.beers', name='beers'),
    
    url(r'^login/', 'Beers.views.login_view', name='login_view'),
    url(r'^login_failed/$', 'Beers.views.login_failed_view', name='login_failed_view'),
    url(r'^logout/', 'Beers.views.logout_view', name='logout_view'),
    
    #url(r'^profile/registerUntappd/?code=(\w+)$', 'Beers.views.register_untappd', name='register_untappd'),
    
    url(r'^profile/checkinBeers/$', 'Beers.views.uploadRatingsToUntappd', name='uploadRatingsToUntappd'),

    url(r'^profile/event_finished/$', 'Beers.views.event_finished', name='event_finished'),
    url(r'^profile/register_foursquare/$', 'Beers.views.register_foursquare', name='register_foursquare'),
    
    url(r'^profile/registerUntappd/$', 'Beers.views.register_untappd', name='register_untappd'),
    url(r'^profile/unregisterUntappd/$', 'Beers.views.unregister_untappd', name='unregister_untappd'),
    url(r'^profile/$', 'Beers.views.profile_view', name='profile_view'),
    
    url(r'^rate_beer/(\d+)$', 'Beers.views.rate_beer', name='rate_beer'),
    
    url(r'^stats/graph/(\d+)$', 'Beers.views.graph', name='graph'),
    url(r'^stats/$', 'Beers.views.stats', name='stats'),

    url(r'^stats/(?P<order_by>\w+)/$', 'Beers.views.stats', name='stats'),
    url(r'^stats/(?P<order_by>\w+)/(?P<desc>\w+)/$', 'Beers.views.stats', name='stats'),
)

urlpatterns += staticfiles_urlpatterns()