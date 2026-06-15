from django.urls import path

from . import views

app_name = "donations"

urlpatterns = [
    path("", views.donate, name="donate"),
    path("callback/", views.payment_callback, name="callback"),
    path("webhook/", views.webhook, name="webhook"),
    path("success/<uuid:token>/", views.success, name="success"),
    path("receipt/<uuid:token>/", views.receipt, name="receipt"),
]
