from django.shortcuts import render, redirect
from .forms import MessageSpecForm
from .models import MessageSpec
from .forms import ReportingEntityForm
from .models import ReportingEntity


def messagespec_create(request):

    form = MessageSpecForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("messagespec_list")

    return render(request, "cbc/messagespec_form.html", {"form": form})


def messagespec_list(request):

    data = MessageSpec.objects.all()

    return render(request, "cbc/messagespec_list.html", {
        "data": data
    })


def reportingentity_create(request):

    form = ReportingEntityForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("reportingentity_list")

    return render(request, "cbc/reportingentity_form.html", {"form": form})


def reportingentity_list(request):

    data = ReportingEntity.objects.all()

    return render(request, "cbc/reportingentity_list.html", {
        "data": data
    })
