from django import template
from Beers.models import Setup

register = template.Library()

@register.tag(name="get_site_name")
def get_site_name():
    site = Setup.objects.all[0]
    return {'site': site.name}