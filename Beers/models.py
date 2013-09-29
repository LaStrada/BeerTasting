from django.db import models
from djangoratings.fields import RatingField

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
    
    rating = RatingField(range=10)
    
    def __unicode__(self):
        return self.name