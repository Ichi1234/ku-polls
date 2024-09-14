"""Urls module for travel to each poll html."""
from django.contrib.admindocs.utils import named_group_matcher
from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),

    path("<int:question_id>/vote/", views.vote, name="vote"),
    path("<int:question_id>/reset/", views.reset_vote, name="reset"),
    ]
