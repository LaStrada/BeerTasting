from django.contrib import admin
from Beers.models import Setup, Brewery, BeerStyle, Beer, BeerRating

admin.autodiscover()

admin.site.register(Setup)
admin.site.register(Brewery)
admin.site.register(BeerStyle)
admin.site.register(Beer)
admin.site.register(BeerRating)