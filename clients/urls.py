from django.urls import path
from .views import releve_client, releve_client_pdf,client_info


urlpatterns = [
    path('client_info/<int:client_id>/', releve_client, name='releve_client'),
    path('releve-client/<int:client_id>/', releve_client, name='releve_client'),
    path('releve-client/<int:client_id>/pdf/', releve_client_pdf, name='releve_client_pdf'),
]