from django.db import models
from django.contrib.auth.models import User

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    role = models.CharField(max_length=20, choices=[('RH','RH'), ('Employe','Employe')], default='Employe')
    # Optionnel : garder le champ date_joined si vous en avez besoin
    date_joined = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"

