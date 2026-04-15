# editions/models.py
from django.db import models

class EditionMenu(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom