from django.contrib import admin
from django.urls import include, path

from polls.views import index

urlpatterns = [
    path("", view=index, name="index"),
]
