from django.urls import path

from . import views

app_name = "volunteers"

urlpatterns = [
    path("", views.opportunity_list, name="list"),
    path("<slug:slug>/", views.opportunity_detail, name="detail"),
]
