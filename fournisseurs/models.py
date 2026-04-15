from django.db import models

class Fournisseur(models.Model):

    nom = models.CharField(max_length=200)
    matricule_fiscal = models.CharField(max_length=50, blank=True, null=True)
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    solde_initial=models.DecimalField(max_digits=12, decimal_places =3, null=True, blank=True,default=0 )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom