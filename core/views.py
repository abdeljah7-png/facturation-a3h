from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import SocieteForm
from .models import Societe


def acceuil(request):
    return render(request, "acceuil.html")


def societe_create(request):

    form = SocieteForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("societe_liste")

    return render(request, "core/societe_form.html", {"form": form})


def societe_liste(request):

    societes = Societe.objects.all()

    return render(request, "core/societe_liste.html", {
        "societes": societes
    })
