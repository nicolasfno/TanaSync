from django.db import models
from employees.models import employee  # ← IMPORT correct

# Create your models here.

class Conge(models.Model):
    employee = models.ForeignKey(employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default='Pending')


class ficheDePaie(models.Model):
    employee = models.ForeignKey(employee, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
