from django.db import models

# Create your models here.
class employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    date_joined = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=[('RH','RH'), ('Employe','Employe')], default='Employe')

