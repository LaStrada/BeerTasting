from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Avg


class Brewery(models.Model):
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name


class BeerStyle(models.Model):
    style = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.style


class Beer(models.Model):
    name = models.CharField(max_length=50)
    brewery = models.ForeignKey(Brewery)
    style = models.ForeignKey(BeerStyle) 
    price = models.IntegerField()
    alcohol = models.FloatField()
    ibu = models.IntegerField()
    
    def get_rating(self):
        rating = BeerRating.objects.filter(beer=self.pk).aggregate(Avg('rating'))
    
    def __unicode__(self):
        return self.name


def validate_rating(value):
    if value > 10 or value < 0:
        raise ValidationError('Not a valid value!')

class BeerRating(models.Model):
    user = models.ForeignKey(User)
    beer = models.ForeignKey(Beer)
    rating = models.IntegerField(validators=[validate_rating])
    comment = models.CharField(max_length=500)
    
    def __unicode__(self):
        return self.rating