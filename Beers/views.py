from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.shortcuts import render, redirect, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db import connection
from django.conf import settings

from Beers.models import Beer, BeerRating, Setup, UntappdUser
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.template import RequestContext, loader
from django.db.models import Count, Avg

import json, requests
from collections import namedtuple

def _json_object_hook(d):
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)

def index(request):
    setup = Setup.objects.get(pk=1)
    return render(request, 'index.html', {'setup':setup})

def beers(request):
    if request.user.is_authenticated():
        setup = Setup.objects.get(pk=1)
        beers = Beer.objects.all()
        ratings = BeerRating.objects.filter(user_id=request.user.id)
        return render(request, 'beers.html', {'setup':setup, 'beers':beers, 'ratings':ratings})

    # if user is not logged in, redirect to index
    return HttpResponseRedirect(reverse('index'))

def stats(request):
    errors = []

    try:
        setup = Setup.objects.get(id=1)
        
        if(setup.finished == True):
            beers = Beer.objects.all()
            
            ratings = BeerRating.objects.raw('''SELECT id, beer_id, ROUND(AVG(CAST(rating AS FLOAT)), 2) AS rating
                                            FROM Beers_beerrating
                                            GROUP BY beer_id
                                            ''')

            #todo: Only show statistics if all the beers have been rated
            #add custom error message
        
            return render(request, 'stats.html', {'beers':beers, 'ratings':ratings})
        else:
            return HttpResponseRedirect(reverse('beers'))
    except:
        #todo: add custom error message
        return HttpResponseRedirect(reverse('index'))

def rate_beer(request, beer_id):
    errors = ''
    beername = []
    c = {}
    c.update(csrf(request))

    setup = Setup.objects.get(id=1)
    
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
                return HttpResponseRedirect(reverse('beers'))
                
            #Insert and return to index
            elif beers.count() == 0:
                new_rating = BeerRating(user=request.user, beer_id=b_id, rating=request.POST['star'],
                                        comment=request.POST['comment'])
                new_rating.save()
                return HttpResponseRedirect(reverse('beers'))
                
            #Too many posts
            else:
                #TODO: Delete posts and create new
                errors = "Too many posts..."
                
        except:
            errors = "Not a valid rating value..."
    
    
    try:
        beer = BeerRating.objects.get(user=request.user.id, beer=b_id)
    except:
        if setup.finished == True:
            beername = Beer.objects.get(pk=b_id)
        else:
            beer = ''
    
    #Change rate button if user has rated this beer before
    if beers.count() > 0:
        rated_before = True
    else:
        rated_before = False
    
    return render(request, 'rate_beer.html', {'beer':beer, 'b_id':b_id, 'errors':errors,
                                              'finished':setup.finished, 'rated_before':rated_before,
                                              'beername':beername})


def login_view(request):
    try:
        c = {}
        c.update(csrf(request))
        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        # Login successful
        if user is not None:
            if user.is_active:
                login(request, user)
                
                return HttpResponseRedirect(reverse('beers'))

            else:
                # Return a 'disabled account' error message
                return HttpResponseRedirect(reverse('login_failed_view'))
        else:
            # Return an 'invalid login' error message.
            return HttpResponseRedirect(reverse('login_failed_view'))
    except:
        return HttpResponseRedirect(reverse('index'))


def register_untappd(request):
    #try:
    if request.GET['code']:
        # verify code
        url =  'https://untappd.com/oauth/authorize/?client_id='
        url += settings.CLIENT_ID + '&client_secret=' + settings.CLIENT_SECRET
        url += '&response_type=code&redirect_url=http://127.0.0.1:8000/profile/registerUntappd/&code=' + request.GET['code']
        
        resp = requests.get(url=url)
        
        data = json.loads(resp.text)
        
        if data['meta']['http_code'] == 200:
            access_token = data['response']['access_token']
        else:
            access_token = ''
        
        
        try:
            untappd_link = UntappdUser.objects.get(pk = request.user)
            untappd_link.untappd = access_token
        except:
            untappd_link = UntappdUser(user=request.user, untappd=access_token)
        
        untappd_link.save()

    return HttpResponseRedirect(reverse('profile_view'))

def unregister_untappd(request):
    untappd_link = UntappdUser.objects.get(pk = request.user)
    untappd_link.untappd = ''
    untappd_link.save()
    
    return HttpResponseRedirect(reverse('profile_view'))


def uploadRatingsToUntappd(request):
    #check if user is linked to Untappd
    if request.user.is_authenticated():
        errors = []
        badges = []
        failed = 0
        uploaded = 0
        url = ''

        numberOfBadges = 0
        numberOfBeers = 0
        
        untappd_link = UntappdUser.objects.get(pk = request.user)
        if untappd_link.untappd == '':
            errors.append('Not linked to untappd.')
        else:
            ratings = BeerRating.objects.filter(user=request.user)
            
            for rating in ratings:
                if rating.uploadedToUntappd != True:
                    """
                    access_token (required) - The access_token for authorized calls
                            (Note: this must be called via a GET parameter:
                            ?access_token=XXXXXX, everything else is a POST parameter)
                    gmt_offset (required) - The numeric value of hours the user is away from the GMT (Greenwich Mean Time)
                    timezone (required) - The timezone of the user, such as EST or PST.
                    bid (required) - The numeric Beer ID you want to check into.
                    foursquare_id (optional) - The MD5 hash ID of the Venue you want to attach the beer checkin.
                            This HAS TO BE the MD5 non-numeric hash from the foursquare v2.
                    foursquare (optional) - Default = "off", Pass "on" to checkin on foursquare
                    shout (optional) - The text you would like to include as a comment of the checkin. Max of 140 characters.
                    rating (optional) - The rating score you would like to add for the beer. This can only be 1 to 5
                            (half ratings are included). You can't rate a beer a 0.
                    """
                    
                    setup = Setup.objects.get(pk=1)
                    untappd = UntappdUser.objects.get(user=request.user)
                    
                    url =  'https://api.untappd.com/v4/checkin/add/?'
                    url += '&access_token=' + untappd.untappd
                    
                    
                    # Create data to post
                    payload = {'gmt_offset': 1,
                               'timezone': 1,
                               'bid': rating.beer.untappdId,
                               'shout': rating.comment,
                               }

                    # Add venue only if all required data is available
                    if setup.geolng and setup.geolat and setup.venue_id:
                        payload['foursquare_id'] = setup.venue_id
                        payload['geolng'] = setup.geolng
                        payload['geolat'] = setup.geolat

                    # Add rating only if rated
                    if rating.rating >= 0 and rating.rating <= 10:
                        payload['rating'] = (str(float(rating.rating) / 2))
                    
                    # Send data and store the response
                    resp = requests.post(url=url, data=payload)
                    
                    # Convert to json
                    data = json.loads(resp.text)
                    
                    try:
                        if data['meta']['code'] == 500:
                            failed += 1
                            # Invalid token, unlink user
                            if data['meta']['error_type'] == 'invalid_token':
                                untappd_link = UntappdUser.objects.get(pk = request.user)
                                untappd_link.untappd = ''
                                untappd_link.save()
                                errors.append(data['meta']['error_detail'])
                                break

                        elif data['response']['result'] == 'success':
                            update_rating = BeerRating.objects.get(pk=rating.id)
                            update_rating.uploadedToUntappd = True
                            update_rating.save()
                            uploaded += 1

                            numberOfBadges += data['response']['badges']['count']

                            for x in range (0, numberOfBadges):
                                badges.append({'name':data['response']['badges']['items'][x]['badge_name'],
                                            'description':data['response']['badges']['items'][x]['badge_description'],
                                            'img':data['response']['badges']['items'][x]['badge_image']['md']})
                        
                    except:
                        pass

        uploaded -= failed
        
        return render(request, 'user/checkinUntappd.html', {'badges':badges, 'uploaded':uploaded,
                                                        'errors':errors, 'numberOfBadges':numberOfBadges,
                                                        'failed':failed})

    # User not logged in
    raise Http404


def profile_view(request):
    if request.user.is_authenticated():
        search = ''
        CLIENT_ID = settings.CLIENT_ID
        
        setup = Setup.objects.get(pk=1)
        
        beers = []
        
        #todo: remove this?
        untappd = False
        
        try:
            u = UntappdUser.objects.get(pk=request.user.id)
            #u = UntappdUser(user=request.user.id)
            if u.untappd:
                untappd = True
        except:
            untappd = False
        finally:
            if request.POST.get('search', False) and request.user.is_superuser:
                search = request.POST['search']
                            
                url =  'https://api.untappd.com/v4/search/beer/?client_id=' + settings.CLIENT_ID
                url += '&client_secret=' + settings.CLIENT_SECRET + '&q=' + search
                
                resp = requests.get(url=url)
                
                data = json.loads(resp.text)
                
                beers = data['response']['beers']['items']
            
            elif (request.POST.get('name', False) and
                        request.POST.get('brewery', False) and
                        request.POST.get('style', False) and
                        request.POST.get('abv', False) and
                        request.POST.get('country', False) and
                        request.POST.get('bid', False)):
                
                new_beer = Beer(name=request.POST['name'], brewery=request.POST['brewery'],
                                style=request.POST['style'], alcohol=float(request.POST['abv']),
                                country=request.POST['country'], label=request.POST['label'],
                                untappdId=request.POST['bid'])
                new_beer.save()

                return HttpResponseRedirect(reverse('beers'))
                
        
        return render(request, 'user/profile.html', {'finished':setup.finished, 'untappd':untappd,
                                                    'beers':beers, 'search':search, 'CLIENT_ID':CLIENT_ID,
                                                    'setup':setup})
    #User not logged in
    raise Http404


def register_foursquare(request):
    errors = ''
    e = []

    # Only admins can change this
    #try:
    if request.user.is_superuser:
        setup = Setup.objects.get(pk=1)

        # check if post data is boolean
        if "foursquare_id" in request.POST:
            if request.POST['foursquare_id'] == '':
                setup.venue_id = ''
            else:
                #search after the untappd venue id
                url =  'https://api.untappd.com/v4/venue/foursquare_lookup/' + request.POST['foursquare_id']
                url += '?client_id=' + settings.CLIENT_ID
                url += '&client_secret=' + settings.CLIENT_SECRET
                resp = requests.get(url=url)
                data = json.loads(resp.text)

                #if True:
                if data['meta']['code'] == 200:
                    if data['response']['venue']['count'] == 1:
                        setup.venue_id = data['response']['venue']['items'][0]['foursquare_id']
                    else:
                        # found more than one place
                        # todo: change to custom error message
                        raise Http404
                else:
                    # json error / wrong request
                    # todo: change to custom error message
                    raise Http404

                if isinstance(request.POST['geolat'], float):
                    setup.geolng = request.POST['geolat']
                else:
                    e['geolat'] = True

                if isinstance(request.POST['geolng'], float):
                    setup.geolng = request.POST['geolng']
                    e['geolng'] = True

                if e['geolng'] or e['geolat']:
                    errors += "Float value is required."

            setup.save()
#    except:
#        raise Http404

    return redirect('profile_view')


def event_finished(request):
    # Only admins can change this
    if request.user.is_superuser:
        setup = Setup.objects.get(pk=1)

        # check if post data is boolean
        if "finished" in request.POST:
            setup.finished = True
        else:
            setup.finished = False
        setup.save()
    return redirect('profile_view')


def logout_view(request):
    logout(request)
    return redirect('index')


def login_failed_view(request):
    setup = Setup.objects.get(pk=1)
    return render(request, 'index_not_logged_in.html', {'setup':setup})