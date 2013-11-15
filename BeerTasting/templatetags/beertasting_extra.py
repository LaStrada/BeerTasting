from django import template
from Beers.models import Setup

register = template.Library()

@register.filter(name="print_stars")
def print_stars(rating):
#     return "lol"
    try:
        int(rating)
        string = ''
        for x in range(0,10):
            if x < rating:
                string += '<span class="glyphicon glyphicon-star"></span>&nbsp;&nbsp;'
            else:
                string += '<span class="glyphicon glyphicon-star-empty"></span>&nbsp;&nbsp;'
            
    except (ValueError, TypeError):
            string = "N/A"
    
    return string
#     return 1

@register.tag(name="get_site_name")
def get_site_name():
    site = Setup.objects.all[0]
    return {'site': site.name}

@register.filter(name="get_range")
def get_range( value ):
    return range( value )