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
    if request.user.is_authenticated():
        beers = Beer.objects.all()
        ratings = BeerRating.objects.filter(user_id=request.user.id)
        setup = Setup.objects.get(pk=1)
        
        return render(request, 'index.html', {'beers':beers, 'ratings':ratings,
                                              'finished':setup.finished})
    
    return render(request, 'index_not_logged_in.html')

def stats(request):
    #try:
        setup = Setup.objects.get(id=1)
        
        if(setup.finished == True):
            beers = Beer.objects.all()
            
            ratings = BeerRating.objects.raw('''SELECT id, beer_id, ROUND(AVG(CAST(rating AS FLOAT)), 2) AS rating
                                            FROM Beers_beerrating
                                            GROUP BY beer_id
                                            ''')
        
            return render(request, 'stats.html', {'beers':beers, 'ratings':ratings})
        else:
            return HttpResponseRedirect(reverse('index'))
    #except:
        #return HttpResponseRedirect(reverse('index'))

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


def register_untappd(request):
    # http://127.0.0.1:8000/profile/registerUntappd/?code=88BF184AE38DA51A1246D55FA6E28765D3F5C8E3
    #try:
    if request.GET['code']:
        #errors = "Successfully linked to untappd."
        
        # verify code
        
        
        
        
        
#         c = pycurl.Curl()
#         c.setopt(pycurl.URL, 'https://untappd.com/oauth/authorize/?client_id=' +
#                  client_code +'&client_secret=' +
#                  client_secret + '&response_type=code&redirect_url=http://127.0.0.1:8000/profile/registerUntappd/&code=' +
#                  request.GET['code'])
#         c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
#         c.setopt(pycurl.VERBOSE, 0)
#         c.perform()
        
        
                    
        url =  'https://untappd.com/oauth/authorize/?client_id=' + settings.CLIENT_ID + '&client_secret=' + settings.CLIENT_SECRET
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
        
        
#         if UntappdUser.objects.filter(pk = request.user).count > 0:
#             untappd_link = UntappdUser.objects.get(pk = request.user)
#             untappd_link.untappd = access_token
#         else:
#             untappd_link = UntappdUser(user=request.user, untappd=access_token)
        
        untappd_link.save()

#finally:
    #errors = "lololol"
    return HttpResponseRedirect(reverse('profile_view'))

def unregister_untappd(request):
    untappd_link = UntappdUser.objects.get(pk = request.user)
    untappd_link.untappd = ''
    untappd_link.save()
    
    return HttpResponseRedirect(reverse('profile_view'))


def uploadRatingsToUntappd(request):
    #check if user is linked to Untappd
    errors = ''
    badges = []
    url = ''
    
    untappd_link = UntappdUser.objects.get(pk = request.user)
    if untappd_link.untappd == '':
        errors = 'Not linked to untappd.'
    else:
        ratings = BeerRating.objects.filter(user=request.user)
        uploaded = 0
        
        for rating in ratings:
            if rating.uploadedToUntappd != True:
                """
                access_token (required) - The access_token for authorized calls (Note: this must be called via a GET parameter - ?access_token=XXXXXX, everything else is a POST parameter)
                gmt_offset (required) - The numeric value of hours the user is away from the GMT (Greenwich Mean Time)
                timezone (required) - The timezone of the user, such as EST or PST.
                bid (required) - The numeric Beer ID you want to check into.
                foursquare_id (optional) - The MD5 hash ID of the Venue you want to attach the beer checkin. This HAS TO BE the MD5 non-numeric hash from the foursquare v2.
                foursquare (optional) - Default = "off", Pass "on" to checkin on foursquare
                shout (optional) - The text you would like to include as a comment of the checkin. Max of 140 characters.
                rating (optional) - The rating score you would like to add for the beer. This can only be 1 to 5 (half ratings are included). You can't rate a beer a 0.
                """
                
                setup = Setup.objects.get(pk=1)
                untappd = UntappdUser.objects.get(user=request.user)
                
                url =  'https://api.untappd.com/v4/checkin/add/?'
#                 url += 'client_id=' + settings.CLIENT_ID
#                 url += '&client_secret=' + settings.CLIENT_SECRET
                url += '&access_token=' + untappd.untappd
                
                
                #payload = '&gmt_offset=1'
                #payload += '&timezone=1'
                #payload += '&bid=' + rating.beer.untappdId
                #if setup.foursquare_id != '':
                #    payload += '&foursquare_id=' + setup.foursquare_id
                #    payload += '&foursquare=yes'
                #if rating.comment != '':
                #    payload += '&shout=' 
                #url += '&rating=' + str(float(rating.rating) / 2)
                
                payload = {'gmt_offset': 1,
                           'timezone': 1,
                           'bid': rating.beer.untappdId,
                           #'bid': '510805b345b04ecf5374ff86',
                           'shout': rating.comment,
                           #'shout': 'test comment',
                           'rating': (str(float(rating.rating) / 2))
                           #'rating': '3.5'
                           }
                
                resp = requests.post(url=url, data=payload)
                
                data = json.loads(resp.text)
                
                try:
                    if data['response']['result'] == 'success':
                        update_rating = BeerRating.objects.get(pk=rating.id)
                        update_rating.uploadedToUntappd = True
                        update_rating.save()
                        uploaded += 1
                    
                        if data['response']['badges'] > 0:
                            badges += data['response']['badges']
                            
                            for b in data['response']['badges']['items']:
                                badges.append({'badge_name': b.badge_name,
                                               'badge_description': b.badge_description,
                                               'lg': b.lg}
                                              )
                except:
                    pass
    
    return render(request, 'user/checkinUntappd.html', {'badges':badges, 'uploaded':uploaded, 'errors':errors})

"""
https://api.untappd.com/v4/checkin/add/
?client_id=EC7EAAB706C553B0691C7DC3C3652CBCAAA1F83B
&client_secret=F02B37BC4644F2C15AB0CF9DFA5A2FE5603AB6D7
&access_token=61CEAA71D1B399C2443B56D67B1D7056ED8C4312
&gmt_offset=1
&timezone=1
&bid=313273
&foursquare_id=510805b345b04ecf5374ff86
&foursquare=yes
&rating=4.0
"""


def profile_view(request):
    search = ''
    
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
        if request.POST.get('search', False):
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
            
            return HttpResponseRedirect(reverse('index'))
            
    
    return render(request, 'user/profile.html', {'finished':setup.finished, 'untappd':untappd, 'beers':beers, 'search':search})


def logout_view(request):
    logout(request)
    return redirect('index')


def login_failed_view(request):
    return render(request, 'index_not_logged_in.html')