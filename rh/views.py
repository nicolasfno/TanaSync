from django.shortcuts import render
from rh.models import Conge, ficheDePaie
from employees.models import EmployeeProfile
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from .utils import create_file  # Assurez-vous d'avoir une fonction pour créer un PDF
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta
import calendar




# Create your views here.
def liste_conges(request):
    if request.method == 'GET':
        conges = Conge.objects.filter(employee_id=request.user.id)
        data = [
            {
                'id': conge.id,
                'start_date': conge.start_date,
                'end_date': conge.end_date,
                'reason': conge.reason,
                'status': conge.status
            }
            for conge in conges
        ]
        return JsonResponse(data, safe=False)

def liste_conges_spe(request, employee_id):
    if request.method == 'GET':
        conges = Conge.objects.filter(employee_id=employee_id)
        data = [
            {
                'id': conge.id,
                'start_date': conge.start_date,
                'end_date': conge.end_date,
                'reason': conge.reason,
                'status': conge.status
            }
            for conge in conges
        ]
        return JsonResponse(data, safe=False)

@csrf_exempt
def modifier_conge(request, id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            conge = Conge.objects.get(id=id)

            # récupérer la valeur envoyée
            statut = data.get("statut", "").lower()

            # déterminer le nouveau statut
            if statut == 'valide':
                conge.status = "Accepté"
            elif statut == "refuse":
                conge.status = "Refusé"
            else:
                return JsonResponse({"error": "Valeur de statut invalide"}, status=400)

            conge.save()
            return JsonResponse({
                "message": f"Congé mis à jour : {conge.status}",
                "id": conge.id,
                "start_date": conge.start_date,
                "end_date": conge.end_date,
                "reason": conge.reason,
                "status": conge.status
            })

        except Conge.DoesNotExist:
            return JsonResponse({"error": "Congé introuvable"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON invalide"}, status=400)



def is_hr(user):
    return user.is_staff or user.groups.filter(name='RH').exists()

@user_passes_test(is_hr)
def create_pay_slip(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        name = request.POST.get('name')
        month = request.POST.get('month')
        year = request.POST.get('year')
        amount = request.POST.get('amount')
        pdf_content = create_file(name, month, year, amount)
        filename = f"bulletin_{month}_{year}.pdf"

        fiche = ficheDePaie(
            employee_id=employee_id,
            month=month,
            year=year,
            amount=amount,
            pdf_file=pdf_content
        )
        fiche.pdf_file.save(filename, pdf_content, save=True)
        return JsonResponse({'message': 'Fiche de paie stockée', 'id': fiche.id})

@user_passes_test(is_hr)
def list_pay_slips(request):
    employee_id = request.GET.get('employee_id')
    if employee_id:
        fiches = ficheDePaie.objects.filter(employee_id=employee_id).order_by('-year', '-month')
    else:
        fiches = ficheDePaie.objects.all().order_by('-uploaded_at')

    data = [
        {
            'id': fiche.id,
            'employee_id': fiche.employee_id,
            'month': fiche.month,
            'year': fiche.year,
            'amount': str(fiche.amount),
            'pdf_url': fiche.pdf_file.url
        }
        for fiche in fiches
    ]
    return JsonResponse(data, safe=False)


@login_required
@user_passes_test(is_hr)
def home_rh(request):
    return render(request, "rh/index.html")

@login_required
@user_passes_test(is_hr)
def vue_equipe(request):
    return render(request, "rh/vue_equipe.html")

@login_required
@user_passes_test(is_hr)
def validation_demandes(request):
    return render(request, "rh/validation_demandes.html")

@login_required
@user_passes_test(is_hr)
def absences_rh(request):
    return render(request, "rh/absences_rh.html")

@login_required
@user_passes_test(is_hr)
def fiches_de_paie_rh(request):
    return render(request, "rh/fiches_de_paie.html")

@login_required
@user_passes_test(is_hr)
def planning_rh(request):
    return render(request, "rh/planning_rh.html")


# ==================== PLANNING GLOBAL ====================

def _get_planning_data(year, month):
    """Construit les données du planning pour un mois donné."""
    employees = EmployeeProfile.objects.filter(role='Employe').select_related('user')
    days_in_month = calendar.monthrange(year, month)[1]
    today = datetime.now().date()

    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }

    avatar_colors = [
        '#FFB6C1', '#DEB887', '#4ECDC4', '#FFB6C1',
        '#FFD95A', '#FF6B9D', '#95E1D3', '#F38181'
    ]

    employees_data = []
    available_count = 0

    for idx, employee in enumerate(employees):
        user = employee.user
        first_initial = user.first_name[0] if user.first_name else ''
        last_initial = user.last_name[0] if user.last_name else ''
        initials = (first_initial + last_initial).upper()
        color = avatar_colors[idx % len(avatar_colors)]

        absences = []
        conges = Conge.objects.filter(
            employee_profile=employee,
            status='Accepté'
        ).filter(
            start_date__year=year,
            start_date__month__lte=month,
            end_date__month__gte=month
        )

        for conge in conges:
            current_date = conge.start_date
            while current_date <= conge.end_date:
                if current_date.month == month and current_date.year == year:
                    absences.append({
                        'date': str(current_date),
                        'type': 'congé',
                        'label': 'Congé'
                    })
                current_date += timedelta(days=1)

        is_available_today = not any(a['date'] == str(today) for a in absences)
        if is_available_today and today.month == month and today.year == year:
            available_count += 1

        # Tableau de jours pour le rendu Django template
        absence_by_date = {a['date']: a for a in absences}
        days_data = []
        for day in range(1, days_in_month + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            if date_str in absence_by_date:
                a = absence_by_date[date_str]
                days_data.append({'has_absence': True, 'type': a['type'], 'label': a['label']})
            else:
                days_data.append({'has_absence': False, 'type': '', 'label': ''})

        employees_data.append({
            'id': employee.id,
            'name': user.get_full_name() or user.username,
            'role': employee.role,
            'avatar_initials': initials,
            'avatar_color': color,
            'available_today': is_available_today,
            'total_days_in_month': days_in_month,
            'absences': absences,
            'days_data': days_data,
        })

    return {
        'month': f'{month_names.get(month, "")} {year}',
        'employees': employees_data,
        'available_count': available_count,
        'total_count': len(employees_data),
        'today': str(today),
        'current_date': str(today),
        'days_in_month': days_in_month,
        'days_range': range(1, days_in_month + 1),
        'current_month': month,
        'year': year,
    }


@login_required
@user_passes_test(is_hr)
def planning_global(request):
    today = datetime.now()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    data = _get_planning_data(year, month)
    data.update({
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })

    return render(request, "rh/planning_global.html", data)


@login_required
@user_passes_test(is_hr)
def export_planning_csv(request):
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))

    data = _get_planning_data(year, month)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="planning_{month}_{year}.csv"'
    response.write('﻿')  # BOM pour Excel

    writer = csv.writer(response)
    writer.writerow(['Employé', 'Rôle'] + [f'Jour {d}' for d in range(1, data['days_in_month'] + 1)])

    for employee in data['employees']:
        row = [employee['name'], employee['role']]
        for day_data in employee['days_data']:
            row.append(day_data['label'] if day_data['has_absence'] else '')
        writer.writerow(row)

    return response


# ==================== API ENDPOINTS ====================

@login_required
@user_passes_test(is_hr)
def api_planning_global(request, year, month):
    """
    API endpoint pour récupérer les données du planning global pour un mois donné.

    Format de réponse:
    {
        "month": "Mai 2026",
        "employees": [
            {
                "id": 1,
                "name": "Jean Dupont",
                "role": "Développeur",
                "avatar_initials": "JD",
                "avatar_color": "#FFB6C1",
                "available_today": true,
                "total_days_in_month": 31,
                "absences": [
                    {
                        "date": "2026-05-08",
                        "type": "congé",
                        "label": "Congé"
                    }
                ]
            }
        ],
        "available_count": 6,
        "total_count": 8,
        "today": "2026-04-28"
    }
    """
    if request.method == 'GET':
        try:
            data = _get_planning_data(year, month)
            return JsonResponse({
                'month': data['month'],
                'employees': [
                    {
                        'id': e['id'],
                        'name': e['name'],
                        'role': e['role'],
                        'avatar_initials': e['avatar_initials'],
                        'avatar_color': e['avatar_color'],
                        'available_today': e['available_today'],
                        'total_days_in_month': e['total_days_in_month'],
                        'absences': e['absences'],
                    }
                    for e in data['employees']
                ],
                'available_count': data['available_count'],
                'total_count': data['total_count'],
                'today': data['today'],
                'current_date': data['current_date'],
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@login_required
@user_passes_test(is_hr)
def api_employees(request):
    """API pour récupérer tous les employés"""
    if request.method == 'GET':
        employees = EmployeeProfile.objects.all().select_related('user')
        data = [
            {
                'id': emp.id,
                'name': emp.user.get_full_name() or emp.user.username,
                'role': emp.role,
                'email': emp.user.email,
                'date_joined': str(emp.date_joined)
            }
            for emp in employees
        ]
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@login_required
@user_passes_test(is_hr)
def api_conges_pending(request):
    """API pour récupérer les congés en attente de validation"""
    if request.method == 'GET':
        conges = Conge.objects.filter(status='Pending').select_related('employee_profile__user')
        data = [
            {
                'id': conge.id,
                'employee_id': conge.employee_profile.id,
                'employee_name': conge.employee_profile.user.get_full_name(),
                'start_date': str(conge.start_date),
                'end_date': str(conge.end_date),
                'reason': conge.reason,
                'status': conge.status
            }
            for conge in conges
        ]
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
