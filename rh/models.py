from django.db import models
from employees.models import EmployeeProfile

# Create your models here.

class Conge(models.Model):
    employee_profile = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, default='Pending')



def user_directory_path(instance, filename):
    # Le fichier sera uploadé dans media/pay_slips/user_<id>/<annee>/<filename>
    return f'pay_slips/user_{instance.employee_profile.user.id}/{instance.year}/{filename}'

class ficheDePaie(models.Model):
    employee_profile = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_file = models.FileField(upload_to=user_directory_path)