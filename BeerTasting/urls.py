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
    
    url(r'^login/', 'Beers.views.login_view', name='login_view'),
    url(r'^login_failed/$', 'Beers.views.login_failed_view', name='login_failed_view'),
    url(r'^logout/', 'Beers.views.logout_view', name='logout_view'),
    
    #url(r'^profile/registerUntappd/?code=(\w+)$', 'Beers.views.register_untappd', name='register_untappd'),
    
    url(r'^profile/registerUntappd/$', 'Beers.views.register_untappd', name='register_untappd'),
    url(r'^profile/unregisterUntappd/$', 'Beers.views.unregister_untappd', name='unregister_untappd'),
    url(r'^profile/$', 'Beers.views.profile_view', name='profile_view'),
    
    url(r'^rate_beer/(\d+)$', 'Beers.views.rate_beer', name='rate_beer'),
    
    url(r'^stats/$', 'Beers.views.stats', name='stats'),
)

urlpatterns += staticfiles_urlpatterns()