from django.contrib import admin
from Beers.models import Setup, Beer, BeerRating, UntappdUser

admin.autodiscover()

admin.site.register(Setup)
admin.site.register(Beer)
admin.site.register(BeerRating)
admin.site.register(UntappdUser)