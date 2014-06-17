from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.shortcuts import render, redirect, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db import connection

from Beers.models import Beer, BeerRating, Setup
from django.core.context_processors import csrf
from django.template import RequestContext, loader
from django.db.models import Count, Avg

def index(request):
    if request.user.is_authenticated():
        beers = Beer.objects.all()
        ratings = BeerRating.objects.filter(user_id=request.user.id)
        setup = Setup.objects.get(pk=1)
        
        return render(request, 'index.html', {'beers':beers, 'ratings':ratings,
                                              'finished':setup.finished})
    
    return render(request, 'index_not_logged_in.html')


def stats(request):
    try:
        setup = Setup.objects.get(pk=1)
        
        if(setup.finished == True):
            beers = Beer.objects.all()
            
            ratings = BeerRating.objects.raw('''SELECT id, beer_id, Cast(AVG(rating as Float)) AS rating
                                            FROM Beers_beerrating
                                            GROUP BY beer_id
                                            ''')
        
            return render(request, 'stats.html', {'beers':beers, 'ratings':ratings})
        else:
            return HttpResponseRedirect(reverse('index'))
    except:
        return HttpResponseRedirect(reverse('index'))
    


def rate_beer(request, beer_id):
    errors = ''
    c = {}
    c.update(csrf(request))
    
    try:
        b_id = int(beer_id)
        
    except:
        raise Http404
    
    beer = Beer.objects.filter(pk=beer_id)
    if beer.count() != 1:
        raise Http404
    
    beers = BeerRating.objects.filter(user=request.user.id, beer=b_id)
    setup = Setup.objects.get(pk=1)
    
    #Validate and store data
    if request.method == 'POST':
        #Validate
        try:
            int(request.POST['star'])
            #Update and return to index
            if beers.count() == 1:
                beer = BeerRating.objects.get(user=request.user.id, beer=b_id)
                
                beer.comment = request.POST['comment']
                beer.rating = int(request.POST['star'])
                beer.save()
                return HttpResponseRedirect(reverse('index'))
                
            #Insert and return to index
            elif beers.count() == 0:
                new_rating = BeerRating(user=request.user, beer_id=b_id, rating=request.POST['star'], comment=request.POST['comment'])
                new_rating.save()
                return HttpResponseRedirect(reverse('index'))
                
            #Too many posts
            else:
                #TODO: Delete posts and create new
                errors = "Too many posts..."
                
        except:
            errors = "Not a valid rating value..."
    
    
    try:
        beer = BeerRating.objects.get(user=request.user.id, beer=b_id)
    except:
        beer = ''
    
    #Change rate button if user has rated this beer before
    if beers.count() > 0:
        rated_before = True
    else:
        rated_before = False
    
    return render(request, 'rate_beer.html', {'beer':beer, 'b_id':b_id, 'errors':errors,
                                              'finished':setup.finished, 'rated_before':rated_before})


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
    return render(request, 'index_not_logged_in.html')