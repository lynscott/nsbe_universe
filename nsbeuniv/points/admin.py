from django.contrib import admin
from . import models
# Register your models here.

class EventInfoInline(admin.TabularInline):
    model = models.Event

admin.site.register(models.Event)
