from django.db import models

class Produit(models.Model):
    reference = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=255)
    p_achat = models.DecimalField(
        "Prix Achat",
        max_digits=12,
        decimal_places=3,
        default=0
    )
    prix_ht = models.DecimalField(max_digits=10, decimal_places=3)
    taux_tva = models.DecimalField(max_digits=4, decimal_places=2, default=19)
    stock_initial = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    seuil = models.IntegerField(default=0)
    date_creation = models.DateField()

    def __str__(self):
        return self.designation