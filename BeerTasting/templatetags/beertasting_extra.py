from django import template
from Beers.models import Setup

register = template.Library()

@register.filter(name="every_other_row")
def every_other_row(row):
    if row % 2:
        return 'active'
    return

@register.filter(name="print_stars")
def print_stars(ratings, b_id):
    rating = 0
    comment = ''
    
    try:
        for r in ratings:
            if int(b_id) == int(r.beer.id):
                rating = int(abs(r.rating))
                comment = r.comment
                break
            
    except (ValueError, TypeError):
        rating = 0
    
    string = ''
    
    for x in range(0,10):
        
        if x < rating:
            string += '<span class="glyphicon glyphicon-star"></span>'
        else:
            string += '<span class="glyphicon glyphicon-star-empty"></span>'
    
    return string

@register.filter(name="print_stars_with_comments")
def print_stars_with_comments(ratings, b_id):
    comment = ''
    
    #todo: Optimize
    for r in ratings:
        if b_id == r.beer_id:
            comment = r.comment
            break
        
    string = print_stars(ratings, b_id)
    
    if comment != '':
        string += "<br />%s" % comment
    
    return string


@register.filter(name="print_stars_form")
def print_stars_form(rating):
    try:
        int(rating)
            
    except (ValueError, TypeError):
        rating = 0
    
    string = '<div id="star">'
    
    for x in range(0,10):
        if (x+1) == rating:
            string += '<input type="radio" name="star" id="%d" value="%d"checked />&nbsp;' % (x, x+1)
            string += '<label for="%d"><span class="glyphicon glyphicon-star"></span></label>' % x
        else:
            string += '<input type="radio" name="star" id="%d" value="%d" />&nbsp;' % (x, x+1)
            string += '<label for="%d"><span class="glyphicon glyphicon-star-empty"></span></label>' % x
    
    string += '</div>'
    
    return string


@register.filter(name="get_site_name")
def get_site_name():
    site = Setup.objects.get(pk=1)
    return site.name