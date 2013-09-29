from django.contrib import admin
from Beers.models import Brewery, BeerStyle, Beer, BeerRating

admin.autodiscover()

admin.site.register(Brewery)
admin.site.register(BeerStyle)
admin.site.register(Beer)
admin.site.register(BeerRating)