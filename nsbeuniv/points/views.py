from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.models import User, Group
from django.views import generic
from django.contrib import messages
from . import models
from . import forms
from braces.views import SelectRelatedMixin

# Create your views here.
class CreateEvent(LoginRequiredMixin, generic.CreateView, PermissionRequiredMixin):
    fields = ('name', 'date', 'location', 'points','info', 'pic', 'url')
    model = models.Event



class EventList(generic.ListView):
    model = models.Event
    context_object_name = 'events'

class EventDetails(generic.DetailView):
    model = models.Event
    context_object_name = 'event_detail'
    template_name = 'points/event_detail.html'

class DeleteEvent(LoginRequiredMixin, generic.DeleteView, PermissionRequiredMixin):
    model = models.Event
    success_url = reverse_lazy('points:events')



    def delete(self, *args, **kwargs):
        messages.success(self.request, "Event Deleted")
        return super().delete(*args, **kwargs)

class UpdateEvent(generic.UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    fields = ('name', 'date', 'location', 'points','info', 'pic', 'url')
    model = models.Event
    
