from django.urls import path

from . import views

app_name = "donations"

urlpatterns = [
    path("", views.donate, name="donate"),
    path("callback/", views.payment_callback, name="callback"),
    path("webhook/", views.webhook, name="webhook"),
    path("success/<int:pk>/", views.success, name="success"),
    path("receipt/<int:pk>/", views.receipt, name="receipt"),
]
