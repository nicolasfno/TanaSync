#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanasync.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import EmployeeProfile
from rh.models import Conge
from datetime import datetime

# Créer les 2 employés manquants
remaining = [
    {'first_name': 'Antoine', 'last_name': 'Delorme', 'email': 'antoine.delorme@tanasync.fr'},
    {'first_name': 'Nathalie', 'last_name': 'Perrin', 'email': 'nathalie.perrin@tanasync.fr'},
]

for emp_data in remaining:
    username = f"{emp_data['first_name'].lower()}.{emp_data['last_name'].lower()}"
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email=emp_data['email'],
            first_name=emp_data['first_name'],
            last_name=emp_data['last_name'],
            password='password123'
        )
        EmployeeProfile.objects.create(user=user, role='Employe')
        print(f"✓ {emp_data['first_name']} {emp_data['last_name']} créé")

# Créer les congés
conges = [
    ('jean.dupont', '2026-05-08', '2026-05-09', 'Congé personnel', 'Accepté'),
    ('sophie.martin', '2026-05-04', '2026-05-06', 'Formation Django', 'Accepté'),
    ('marc.dubois', '2026-05-02', '2026-05-02', 'Télétravail', 'Accepté'),
    ('marc.dubois', '2026-05-15', '2026-05-16', 'Congé', 'Accepté'),
    ('emma.bernard', '2026-05-12', '2026-05-13', 'Congé personnel', 'Accepté'),
    ('lucas.petit', '2026-05-20', '2026-05-20', 'Repos', 'Pending'),
    ('antoine.delorme', '2026-05-10', '2026-05-10', 'Congé personnel', 'Pending'),
]

for username, start, end, reason, status in conges:
    try:
        user = User.objects.get(username=username)
        # Créer le profil s'il n'existe pas
        emp, created = EmployeeProfile.objects.get_or_create(user=user, defaults={'role': 'Employe'})
        
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        
        if not Conge.objects.filter(employee_profile=emp, start_date=start_date, end_date=end_date).exists():
            Conge.objects.create(
                employee_profile=emp,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status=status
            )
            print(f"✓ Congé: {user.get_full_name()} ({start})")
    except User.DoesNotExist:
        print(f"✗ Utilisateur non trouvé: {username}")

print("\n✅ Données de test créées avec succès!")
