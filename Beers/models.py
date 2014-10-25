from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Avg


class UntappdUser(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    untappd = models.CharField(max_length=100, blank=True)
    
    #todo: only one instance per user!


def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 0 and
        obj.id != model.objects.get().id):
        raise ValidationError("Can only create 1 %s instance" % model.__name__)
    
class Setup(models.Model):
    name = models.CharField(max_length=50)
    intro = models.TextField(blank=True)
    finished = models.BooleanField()
    venue_id = models.CharField(max_length=50, blank=True)
    geolat = models.FloatField(default=0)
    geolng = models.FloatField(default=0)
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        validate_only_one_instance(self)


class Beer(models.Model):
    name = models.CharField(max_length=50)
    brewery = models.CharField(max_length=50)
    style = models.CharField(max_length=50) 
    label = models.CharField(max_length=200)
    alcohol = models.FloatField()
    country = models.CharField(max_length=50)
    untappdId = models.CharField(max_length=50)
    #ibu = models.IntegerField()
    
    def get_rating(self):
        rating = BeerRating.objects.filter(beer=self.pk).aggregate(Avg('rating'))
    
    def __unicode__(self):
        return unicode(self.name)


def validate_rating(value):
    if value > 10 or value < 0:
        raise ValidationError('Not a valid value!')

class BeerRating(models.Model):
    user = models.ForeignKey(User)
    beer = models.ForeignKey(Beer, related_name='ratings')
    rating = models.IntegerField(validators=[validate_rating])
    comment = models.CharField(max_length=140, blank=True)
    uploadedToUntappd = models.BooleanField(default=False)
    
    def __unicode__(self):
        return unicode("User: %s, Beer: %s, Rating: %d" % (self.user, self.beer, self.rating))