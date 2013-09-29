from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.views import login, logout
from django.shortcuts import render, redirect, render_to_response
from django.http import Http404, HttpResponseRedirect

from Beers.models import Beer

def index(request):
    beers = Beer.objects.all()
    return render(request, 'index.html', {'beers':beers, 'login_failed':False})


def selected_beer(request, id):
    beer = Beer.objects.get(pk=id)
    return render(request, 'selected_beer.html', {'beer':beer})


def stats(request):
    return render(request, 'stats.html')


def login_view(request):
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