from django.urls import path
from .views import acceuil
from django.urls import path
from . import views



urlpatterns = [
    path("", acceuil, name="acceuil"),
    path("societes/", views.societe_liste, name="societe_liste"),
    path("societes/nouveau/", views.societe_create, name="societe_create"),
]