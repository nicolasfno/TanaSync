from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import EmployeeProfile
from rh.models import Conge
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Crée des utilisateurs de test et des congés'

    def handle(self, *args, **options):
        # Données des employés
        employees_data = [
            {'first_name': 'Jean', 'last_name': 'Dupont', 'email': 'jean.dupont@tanasync.fr', 'role': 'Employe'},
            {'first_name': 'Sophie', 'last_name': 'Martin', 'email': 'sophie.martin@tanasync.fr', 'role': 'Employe'},
            {'first_name': 'Marc', 'last_name': 'Dubois', 'email': 'marc.dubois@tanasync.fr', 'role': 'Employe'},
            {'first_name': 'Emma', 'last_name': 'Bernard', 'email': 'emma.bernard@tanasync.fr', 'role': 'Employe'},
            {'first_name': 'Lucas', 'last_name': 'Petit', 'email': 'lucas.petit@tanasync.fr', 'role': 'Employe'},
            {'first_name': 'Julie', 'last_name': 'Moreau', 'email': 'julie.moreau@tanasync.fr', 'role': 'Employe'},
            {'first_name': 'Antoine', 'last_name': 'Delorme', 'email': 'antoine.delorme@tanasync.fr', 'role': 'Employe'},
            {'first_name': 'Nathalie', 'last_name': 'Perrin', 'email': 'nathalie.perrin@tanasync.fr', 'role': 'Employe'},
        ]

        # Créer les utilisateurs et profils
        created_count = 0
        for emp_data in employees_data:
            username = f"{emp_data['first_name'].lower()}.{emp_data['last_name'].lower()}"
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=emp_data['email'],
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name'],
                    password='password123'
                )
                EmployeeProfile.objects.create(
                    user=user,
                    role=emp_data['role']
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Créé: {emp_data["first_name"]} {emp_data["last_name"]}'))
            else:
                self.stdout.write(f'  Déjà existant: {username}')

        # Créer des congés de test
        conges_data = [
            {
                'employee_username': 'jean.dupont',
                'start_date': datetime(2026, 5, 8).date(),
                'end_date': datetime(2026, 5, 9).date(),
                'reason': 'Congé personnel',
                'status': 'Accepté'
            },
            {
                'employee_username': 'sophie.martin',
                'start_date': datetime(2026, 5, 4).date(),
                'end_date': datetime(2026, 5, 6).date(),
                'reason': 'Formation Django',
                'status': 'Accepté'
            },
            {
                'employee_username': 'marc.dubois',
                'start_date': datetime(2026, 5, 2).date(),
                'end_date': datetime(2026, 5, 2).date(),
                'reason': 'Télétravail',
                'status': 'Accepté'
            },
            {
                'employee_username': 'marc.dubois',
                'start_date': datetime(2026, 5, 15).date(),
                'end_date': datetime(2026, 5, 16).date(),
                'reason': 'Congé',
                'status': 'Accepté'
            },
            {
                'employee_username': 'emma.bernard',
                'start_date': datetime(2026, 5, 12).date(),
                'end_date': datetime(2026, 5, 13).date(),
                'reason': 'Congé personnel',
                'status': 'Accepté'
            },
            {
                'employee_username': 'lucas.petit',
                'start_date': datetime(2026, 5, 20).date(),
                'end_date': datetime(2026, 5, 20).date(),
                'reason': 'Repos',
                'status': 'Pending'
            },
            {
                'employee_username': 'antoine.delorme',
                'start_date': datetime(2026, 5, 10).date(),
                'end_date': datetime(2026, 5, 10).date(),
                'reason': 'Congé personnel',
                'status': 'Pending'
            },
        ]

        conges_created = 0
        for conge_data in conges_data:
            try:
                user = User.objects.get(username=conge_data['employee_username'])
                employee_profile = user.employee_profile
                
                # Vérifier que le congé n'existe pas déjà
                exists = Conge.objects.filter(
                    employee_profile=employee_profile,
                    start_date=conge_data['start_date'],
                    end_date=conge_data['end_date']
                ).exists()
                
                if not exists:
                    Conge.objects.create(
                        employee_profile=employee_profile,
                        start_date=conge_data['start_date'],
                        end_date=conge_data['end_date'],
                        reason=conge_data['reason'],
                        status=conge_data['status']
                    )
                    conges_created += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Congé créé: {user.get_full_name()} ({conge_data["start_date"]})'
                    ))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ Utilisateur non trouvé: {conge_data["employee_username"]}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n=== Résumé ===\n{created_count} utilisateurs créés\n{conges_created} congés créés'
        ))
