from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.shortcuts import render, redirect, render_to_response
from django.http import Http404, HttpResponseRedirect
from django.db import connection

from Beers.models import Beer, BeerRating
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.db.models import Count

def index(request):
    beers = Beer.objects.all()
#    beers = BeerRating.objects.raw('''SELECT *
#                                FROM Beers_beer
#                                LEFT JOIN Beers_beerrating
#                                ON Beers_beer.id=Beers_beerrating.beer_id''')
    
    ratings = BeerRating.objects.filter(user_id=request.user.id)
    
    return render(request, 'index.html', {'beers':beers, 'ratings':ratings, 'login_failed':False, 'Finished':False})


def stats(request):
    beers = Beer.objects.raw('SELECT * FROM Beers_beer LEFT JOIN Beers_beerrating ON Beers_beer.id=Beers_beerrating.beer_id')
    
    return render(request, 'index.html', {'beers':beers, 'login_failed':False, 'finished':True})


def rate_beer(request, beer_id):
    errors = ''
    c = {}
    c.update(csrf(request))
    
    try:
        b_id = int(beer_id)
        
    except:
        raise Http404
    
    beers = BeerRating.objects.filter(user=request.user.id, beer=b_id)
    
    #Validate and store data
    if request.method == 'POST':
        #Validate
        #todo: validate message and rating
        if int(request.POST['star']):
            #Update
            if beers.count() == 1:
                beer = BeerRating.objects.get(user=request.user.id, beer=b_id)
                
                beer.comment = request.POST['comment']
                beer.rating = int(request.POST['star'])
                beer.save()
                return HttpResponseRedirect(reverse('index'))
                
            #Insert
            elif beers.count() == 0:
                new_rating = BeerRating(user=request.user, beer_id=b_id, rating=request.POST['star'], comment=request.POST['comment'])
                new_rating.save()
                return HttpResponseRedirect(reverse('index'))
                
            #Too many posts
            else:
                errors = "Too many posts..."
                
        else:
            errors = "Not a valid rating value..."
    
    
    try:
        beer = BeerRating.objects.get(user=request.user.id, beer=b_id)
    except:
        raise Http404
    
    return render(request, 'rate_beer.html', {'beer':beer, 'b_id':b_id, 'errors':errors})


def login_view(request):
    c = {}
    c.update(csrf(request))
    
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    
    if user is not None:
        if user.is_active:
            login(request, user)
            
            return HttpResponseRedirect(reverse('index'))

        else:
            # Return a 'disabled account' error message
            return HttpResponseRedirect(reverse('login_failed_view'))
    else:
        # Return an 'invalid login' error message.
        return HttpResponseRedirect(reverse('login_failed_view'))


def profile_view(request):
    return render(request, 'user/profile.html')


def logout_view(request):
    logout(request)
    return redirect('index')


def login_failed_view(request):
    beers = Beer.objects.all()
    return render(request, 'index.html', {'beers':beers, 'login_failed':True})