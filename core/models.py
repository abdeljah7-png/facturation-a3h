from django.db import models

class Societe(models.Model):

    nom = models.CharField(max_length=200)
    matricule_fiscal = models.CharField(max_length=50)

    pays = models.CharField(max_length=2)  # OK (TN, FR, etc.)

    adresse = models.CharField(max_length=300)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=20)

    telephone = models.CharField(max_length=20)
    email = models.EmailField()

    date_creation = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nom

def save(self, *args, **kwargs):
    if not self.pk and Societe.objects.exists():
        raise Exception("Une seule société est autorisée")
    super().save(*args, **kwargs)
