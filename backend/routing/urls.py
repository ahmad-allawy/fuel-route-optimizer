from django.contrib import admin
from django.urls import path

from routing.views import RouteFuelAPIView

urlpatterns = [
    path('route-fuel/',RouteFuelAPIView.as_view(), name='route-fuel'),
]
