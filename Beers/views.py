from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.shortcuts import render, redirect, render_to_response
from django.http import Http404, HttpResponseRedirect
from django.db import connection

from Beers.models import Beer
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.template import RequestContext, loader

def index(request):
    #beers = Beer.objects.all()
    beers = Beer.objects.raw('SELECT * FROM Beers_beer LEFT JOIN Beers_beerrating ON Beers_beer.id=Beers_beerrating.beer_id')
    return render(request, 'index.html', {'beers':beers, 'login_failed':False, 'Finished':True})


def selected_beer(request):
    #beer = Beer.objects.all()
    #ratings = BeerRating.objects.all().filter(user=1)
    #beer = Beer.objects.all().prefetch_related('id__id')
    #beers = Beer.objects.select_related('rating')
    #beers = Beer.objects.all().prefetch_related('ratings') 
    
#     beers = Beer.objects.raw('SELECT * FROM Beers_beer LEFT JOIN Beers_beerrating ON Beers_beer.id=Beers_beerrating.beer_id')
    
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Beers_beer LEFT JOIN Beers_beerrating ON Beers_beer.id=Beers_beerrating.beer_id")
    a = cursor.fetchall()
    
    return render(request, 'selected_beer.html', {'beers':beers})


def stats(request):
    return render(request, 'stats.html')


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