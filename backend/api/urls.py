from django.contrib import admin
from . import views
from django.urls import path
# from content import views as c_views

# use as_view only if it is a Class based view not Function Based view

urlpatterns = [
    path("experience/<int:id>", views.ExperienceView.as_view(), name="experience"),
    path(
        "experience/category/<str:category>/",
        views.ExperienceCategoryView.as_view(),
        name="category",
    ),
    path("location/", views.LocationView.as_view(), name="location"),
    path("experiences/", views.ExperienceViewList.as_view(), name="experinence_list"),
]
