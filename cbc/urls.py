from django.urls import path
from . import views

urlpatterns = [

    # MessageSpec
    path("messagespec/", views.messagespec_list, name="messagespec_list"),
    path("messagespec/nouveau/", views.messagespec_create, name="messagespec_create"),

    # ReportingEntity
    path("reportingentity/", views.reportingentity_list, name="reportingentity_list"),
    path("reportingentity/nouveau/", views.reportingentity_create, name="reportingentity_create"),

]