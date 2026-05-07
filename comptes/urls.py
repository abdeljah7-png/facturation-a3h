from django.urls import path
from .views import releve_compte,releve_compte_pdf, releve_non_echu, releve_non_echu_pdf


urlpatterns = [
    path("releve/<int:compte_id>/", releve_compte, name="releve_compte"),
    path(
        "releve/<int:compte_id>/pdf/",
        releve_compte_pdf,
        name="releve_compte_pdf",
    ),
    path("releve/non-echu/<int:compte_id>/", releve_non_echu, name="releve_non_echu"),
    path("releve/non-echu/<int:compte_id>/pdf/", releve_non_echu_pdf, name="releve_non_echu_pdf"),
]

 



