from django import template
from Beers.models import Setup
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def navactive(request, urls):
	if request.path in ( reverse(url) for url in urls.split() ):
		return ' class="active"'
	return ""


@register.filter(name="every_other_row")
def every_other_row(row):
	if row % 2:
		return 'active'
	return

@register.filter(name="print_stars")
def print_stars(ratings, b_id):
	string = ''
	rating = 0
	
	try:
		for r in ratings:
			if int(b_id) == int(r.beer.id):
				rat = r.rating
				rating = int(abs(round(r.rating)))
				break
			
	except (ValueError, TypeError):
		rating = 0
	
	for x in range(0,10):
		
		if x < rating:
			string += '<span class="star glyphicon glyphicon-star"></span>'
		else:
			string += '<span class="star glyphicon glyphicon-star-empty"></span>'
	
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
		int(round(rating))
			
	except (ValueError, TypeError):
		rating = 0
	
	string = '<div id="star">'
	
	for x in range(0,10):
		if (x+1) == rating:
			string += '<input type="radio" name="star" id="%d" value="%d" checked />&nbsp;' % (x, x+1)
			string += '<label for="%d"><span class="star glyphicon glyphicon-star"></span></label>' % x
		else:
			string += '<input type="radio" name="star" id="%d" value="%d" />&nbsp;' % (x, x+1)
			string += '<label for="%d"><span class="star glyphicon glyphicon-star-empty"></span></label>' % x
	
	string += '</div>'
	
	return string


@register.filter(name="return_with_decimal")
def return_with_decimal(ratings, b_id):
	try:
		for r in ratings:
			if int(b_id) == int(r.beer.id):
				rating = float(r.rating)
				break
			
	except (ValueError, TypeError):
		rating = 0
		
	if int(rating):
		return float(round(rating, 1))
	else:
		return 'N/A'


@register.filter(name="get_site_name")
def get_site_name():
	site = Setup.objects.get(pk=1)
	return site.name


@register.filter(name="untappd_ok")
def untappd_ok(ratings, b_id):
	#todo: Optimize
	for r in ratings:
		if b_id == r.beer_id:
			if r.uploadedToUntappd:
				return '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'
			else:
				break
	return '&nbsp;'