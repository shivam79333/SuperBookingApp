from django.contrib import admin
from . import views
from django.urls import path

urlpatterns = [
    path("experience/<id>", views.ExperienceView.as_view(), name="experience"),
]
