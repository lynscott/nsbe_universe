#Points urls
from django.conf.urls import url
from points import views
from django.contrib.auth.decorators import permission_required

app_name = 'points'

urlpatterns = [
    url(r'^$', views.EventList.as_view(), name='events' ),
    url(r'^(?P<pk>\d+)/$',views.EventDetails.as_view(),name='detail'),
    url(r'^new/$',(views.CreateEvent.as_view()), name='create'),
    url(r'update/(?P<pk>\d+)/$', (views.UpdateEvent.as_view()), name='update'),
    url(r'delete/(?P<pk>\d+)$',(views.DeleteEvent.as_view()), name='delete'),
    ]
