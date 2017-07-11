from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.text import slugify


from django import template
register = template.Library()



# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=256)
    date = models.DateField(blank=True)
    location = models.CharField(max_length=256)
    points = models.PositiveIntegerField()
    info = models.TextField(blank=True)
    pic = models.ImageField(upload_to='event_pics', blank=True)
    url = models.URLField(blank = True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("points:detail", kwargs={'pk':self.pk})

    class Meta:
        ordering = ['-date']
