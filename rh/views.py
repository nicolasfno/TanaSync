from django.shortcuts import render, redirect
from django.urls import reverse
from rh.models import Conge, ficheDePaie
from employees.models import EmployeeProfile
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, FileResponse
import os
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from .utils import create_file
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

@login_required
@user_passes_test(is_hr)
def create_pay_slip(request):
    if request.method == 'POST':
        employee_profile_id = request.POST.get('employee_id')
        month = request.POST.get('month')
        year = request.POST.get('year')
        amount = request.POST.get('amount')
        profile = EmployeeProfile.objects.select_related('user').get(id=employee_profile_id)
        name = profile.user.get_full_name() or profile.user.username
        pdf_content = create_file(name, month, year, amount)
        filename = f"bulletin_{month}_{year}.pdf"
        fiche = ficheDePaie(
            employee_profile_id=employee_profile_id,
            month=month, year=year, amount=amount,
        )
        fiche.pdf_file.save(filename, pdf_content, save=True)
        return redirect('fiches_de_paie_rh')
    return redirect('fiches_de_paie_rh')

@login_required
@user_passes_test(is_hr)
def view_pay_slip_rh(request, fiche_id):
    fiche = ficheDePaie.objects.get(id=fiche_id)
    path = fiche.pdf_file.path
    filename = os.path.basename(path)
    response = FileResponse(open(path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

@login_required
@user_passes_test(is_hr)
def download_pay_slip_rh(request, fiche_id):
    fiche = ficheDePaie.objects.get(id=fiche_id)
    path = fiche.pdf_file.path
    filename = os.path.basename(path)
    response = FileResponse(open(path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@user_passes_test(is_hr)
def list_pay_slips(request):
    employee_id = request.GET.get('employee_id')
    if employee_id:
        fiches = ficheDePaie.objects.filter(employee_id=employee_id).order_by('-year', '-month')
    else:
        fiches = ficheDePaie.objects.all().order_by('-year', '-id')

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
    from datetime import date
    today = date.today()

    total_employees = EmployeeProfile.objects.count()
    pending_count = Conge.objects.filter(status='Pending').count()

    on_leave_today = Conge.objects.filter(
        status='Accepté',
        start_date__lte=today,
        end_date__gte=today,
    ).values('employee_profile').distinct().count()

    pending_conges_qs = Conge.objects.filter(
        status='Pending'
    ).select_related('employee_profile__user').order_by('-created_at')[:5]

    pending_conges = []
    for idx, conge in enumerate(pending_conges_qs):
        user = conge.employee_profile.user
        first_initial = user.first_name[0] if user.first_name else ''
        last_initial = user.last_name[0] if user.last_name else ''
        days = (conge.end_date - conge.start_date).days + 1
        pending_conges.append({
            'id': conge.id,
            'employee_name': user.get_full_name() or user.username,
            'avatar_initials': (first_initial + last_initial).upper(),
            'avatar_color': AVATAR_COLORS[idx % len(AVATAR_COLORS)],
            'type_label': _get_conge_type_label(conge.reason),
            'start_date': _format_date_fr(conge.start_date),
            'end_date': _format_date_fr(conge.end_date),
            'days': days,
            'reason': conge.reason,
            'created_at': _format_date_fr(conge.created_at.date()) if conge.created_at else '',
        })

    return render(request, "rh/index.html", {
        'total_employees': total_employees,
        'pending_count': pending_count,
        'on_leave_today': on_leave_today,
        'pending_conges': pending_conges,
    })

@login_required
@user_passes_test(is_hr)
def vue_equipe(request):
    return render(request, "rh/vue_equipe.html")

MONTH_NAMES_FR = {
    1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
    5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
    9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
}

AVATAR_COLORS = [
    '#FFB6C1', '#DEB887', '#4ECDC4', '#C3A6FF',
    '#FFD95A', '#FF6B9D', '#95E1D3', '#F38181'
]

QUOTA_ANNUEL = 25

TYPES_ABSENCE = [
    ('Congé payé', 'Congé payé'),
    ('RTT', 'RTT'),
    ('Formation', 'Formation'),
    ('Maladie', 'Maladie'),
    ('Repos', 'Repos'),
]


def _get_conge_type_label(reason):
    """Détermine le label du type de congé à partir du motif."""
    r = reason.lower()
    if 'formation' in r:
        return 'Formation'
    if 'maladie' in r or 'arrêt' in r:
        return 'Maladie'
    if 'rtt' in r or 'repos' in r or 'télétravail' in r or 'pont' in r:
        return 'RTT'
    return 'Congé payé'


def _format_date_fr(date):
    """Formate une date en français: '15 Mai 2025'."""
    return f"{date.day} {MONTH_NAMES_FR[date.month]} {date.year}"


def _build_absences_context(profile, tab):
    """
    Construit le contexte partagé pour la page de demande d'absence.
    Utilisé par employees.views.mes_absences ET rh.views.absences_rh
    pour éviter toute duplication de logique.
    """
    from datetime import date as dt_date
    today = dt_date.today()

    conges_qs = Conge.objects.filter(
        employee_profile=profile
    ).order_by('-created_at', '-start_date')

    # Calcul du solde annuel
    jours_pris = sum(
        (c.end_date - c.start_date).days + 1
        for c in conges_qs.filter(status='Accepté', start_date__year=today.year)
    )
    jours_en_attente = sum(
        (c.end_date - c.start_date).days + 1
        for c in conges_qs.filter(status='Pending')
    )

    conges_data = []
    for conge in conges_qs:
        days = (conge.end_date - conge.start_date).days + 1
        conges_data.append({
            'id': conge.id,
            'type_label': _get_conge_type_label(conge.reason),
            'start_date': _format_date_fr(conge.start_date),
            'end_date': _format_date_fr(conge.end_date),
            'days': days,
            'reason': conge.reason,
            'status': conge.status,
            'created_at': _format_date_fr(conge.created_at.date()) if conge.created_at else '',
        })

    return {
        'tab': tab,
        'conges': conges_data,
        'types_absence': TYPES_ABSENCE,
        'jours_pris': jours_pris,
        'jours_restants': max(0, QUOTA_ANNUEL - jours_pris),
        'jours_en_attente': jours_en_attente,
        'quota_annuel': QUOTA_ANNUEL,
    }


@login_required
@user_passes_test(is_hr)
def validation_demandes(request):
    tab = request.GET.get('tab', 'a_valider')

    if tab == 'historique':
        conges_qs = Conge.objects.filter(
            status__in=['Accepté', 'Refusé']
        ).select_related('employee_profile__user').order_by('-created_at')
    elif tab == 'toutes':
        conges_qs = Conge.objects.all().select_related(
            'employee_profile__user'
        ).order_by('-created_at')
    else:
        conges_qs = Conge.objects.filter(
            status='Pending'
        ).select_related('employee_profile__user').order_by('-created_at')

    pending_count = Conge.objects.filter(status='Pending').count()

    conges_data = []
    for idx, conge in enumerate(conges_qs):
        user = conge.employee_profile.user
        first_initial = user.first_name[0] if user.first_name else ''
        last_initial = user.last_name[0] if user.last_name else ''
        days = (conge.end_date - conge.start_date).days + 1

        conges_data.append({
            'id': conge.id,
            'employee_name': user.get_full_name() or user.username,
            'avatar_initials': (first_initial + last_initial).upper(),
            'avatar_color': AVATAR_COLORS[idx % len(AVATAR_COLORS)],
            'type_label': _get_conge_type_label(conge.reason),
            'start_date': _format_date_fr(conge.start_date),
            'end_date': _format_date_fr(conge.end_date),
            'days': days,
            'reason': conge.reason,
            'status': conge.status,
            'created_at': _format_date_fr(conge.created_at.date()) if conge.created_at else '',
        })

    return render(request, "rh/validation_demandes.html", {
        'conges': conges_data,
        'pending_count': pending_count,
        'tab': tab,
    })


@login_required
@user_passes_test(is_hr)
def traiter_conge(request, id):
    if request.method == 'POST':
        action = request.POST.get('action')
        tab = request.POST.get('tab', 'a_valider')
        try:
            conge = Conge.objects.get(id=id)
            if action == 'approuver':
                conge.status = 'Accepté'
            elif action == 'refuser':
                conge.status = 'Refusé'
            conge.save()
        except Conge.DoesNotExist:
            pass
        return redirect(reverse('validation_demandes') + f'?tab={tab}')
    return redirect('validation_demandes')

@login_required
@user_passes_test(is_hr)
def absences_rh(request):
    try:
        profile = request.user.employee_profile
    except Exception:
        # Superuser sans profil employé : créer un profil RH à la volée
        from employees.models import EmployeeProfile
        profile, _ = EmployeeProfile.objects.get_or_create(
            user=request.user, defaults={'role': 'RH'}
        )
    tab = request.GET.get('tab', 'nouvelle')

    if request.method == 'POST':
        type_absence = request.POST.get('type_absence', '')
        commentaire = request.POST.get('commentaire', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = f"{type_absence} - {commentaire}" if commentaire else type_absence
        Conge.objects.create(
            employee_profile=profile,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        return redirect(reverse('absences_rh') + '?tab=mes_demandes')

    context = _build_absences_context(profile, tab)
    context['cancel_url_name'] = 'rh_annuler_conge'
    return render(request, "rh/absences_rh.html", context)


@login_required
@user_passes_test(is_hr)
def rh_annuler_conge(request, id):
    if request.method == 'POST':
        try:
            conge = Conge.objects.get(id=id, employee_profile__user=request.user)
            conge.delete()
        except Conge.DoesNotExist:
            pass
    return redirect(reverse('absences_rh') + '?tab=mes_demandes')

@login_required
@user_passes_test(is_hr)
def fiches_de_paie_rh(request):
    q = request.GET.get('q', '').strip()
    try:
        selected_year = int(request.GET.get('year', ''))
    except (ValueError, TypeError):
        selected_year = None

    profiles = EmployeeProfile.objects.select_related('user').order_by('user__last_name')
    if q:
        profiles = profiles.filter(
            Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
        )

    employees_data = []
    for idx, profile in enumerate(profiles):
        fiches = ficheDePaie.objects.filter(employee_profile=profile).order_by('-year', '-id')
        if selected_year:
            fiches = fiches.filter(year=selected_year)
        employees_data.append({
            'id': profile.id,
            'name': profile.user.get_full_name() or profile.user.username,
            'initials': (
                (profile.user.first_name[0] if profile.user.first_name else '') +
                (profile.user.last_name[0] if profile.user.last_name else '')
            ).upper(),
            'avatar_color': AVATAR_COLORS[idx % len(AVATAR_COLORS)],
            'fiches': list(fiches),
        })

    years = ficheDePaie.objects.values_list('year', flat=True).distinct().order_by('-year')

    return render(request, "rh/fiches_de_paie.html", {
        'employees_data': employees_data,
        'all_profiles': EmployeeProfile.objects.select_related('user').order_by('user__last_name'),
        'month_names': MONTH_NAMES_FR,
        'current_year': datetime.now().year,
        'q': q,
        'selected_year': selected_year,
        'years': years,
    })

@login_required
@user_passes_test(is_hr)
def planning_rh(request):
    from datetime import date, timedelta
    import calendar as cal_lib

    try:
        profile = request.user.employee_profile
    except Exception:
        from employees.models import EmployeeProfile
        profile, _ = EmployeeProfile.objects.get_or_create(user=request.user, defaults={'role': 'RH'})

    try:
        month = int(request.GET.get('month', 0)) or None
        year  = int(request.GET.get('year',  0)) or None
    except (ValueError, TypeError):
        month, year = None, None

    today = date.today()
    year  = year  or today.year
    month = month or today.month
    last_day = cal_lib.monthrange(year, month)[1]

    conges_acceptes = Conge.objects.filter(
        employee_profile=profile,
        status='Accepté',
        start_date__lte=date(year, month, last_day),
        end_date__gte=date(year, month, 1),
    )
    conge_days = set()
    for c in conges_acceptes:
        cur = max(c.start_date, date(year, month, 1))
        fin = min(c.end_date, date(year, month, last_day))
        while cur <= fin:
            conge_days.add(cur.day)
            cur += timedelta(days=1)

    MOIS_FR = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    cal = cal_lib.Calendar(firstweekday=6)

    prev_month = 12 if month == 1 else month - 1
    prev_year  = year - 1 if month == 1 else year
    next_month = 1  if month == 12 else month + 1
    next_year  = year + 1 if month == 12 else year

    return render(request, "rh/planning_rh.html", {
        'month_days':    cal.monthdayscalendar(year, month),
        'today':         today.day if (today.year == year and today.month == month) else -1,
        'cal_month_name': f"{MOIS_FR[month]} {year}",
        'conge_days':    conge_days,
        'cal_prev_url':  reverse('planning_rh') + f"?month={prev_month}&year={prev_year}",
        'cal_next_url':  reverse('planning_rh') + f"?month={next_month}&year={next_year}",
    })


# ==================== PLANNING GLOBAL ====================

def _get_absence_type(reason):
    """Détermine le type d'absence à partir du motif."""
    r = reason.lower()
    if 'formation' in r:
        return 'formation'
    if 'maladie' in r or 'arrêt' in r:
        return 'maladie'
    if 'repos' in r or 'télétravail' in r:
        return 'repos'
    return 'congé'


def _get_planning_data(year, month, team='all', absence_type='all'):
    """Construit les données du planning pour un mois donné."""

    # Filtrer les employés selon l'équipe sélectionnée
    if team == 'rh':
        employees = EmployeeProfile.objects.filter(role='RH').select_related('user')
    elif team == 'employes':
        employees = EmployeeProfile.objects.filter(role='Employe').select_related('user')
    else:
        employees = EmployeeProfile.objects.all().select_related('user')

    days_in_month = calendar.monthrange(year, month)[1]
    today = datetime.now().date()

    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }

    type_labels = {
        'congé': 'Congé',
        'formation': 'Formation',
        'maladie': 'Maladie',
        'repos': 'Repos',
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
            abs_type = _get_absence_type(conge.reason)

            # Appliquer le filtre par type d'absence
            if absence_type != 'all' and abs_type != absence_type:
                continue

            current_date = conge.start_date
            while current_date <= conge.end_date:
                if current_date.month == month and current_date.year == year:
                    absences.append({
                        'date': str(current_date),
                        'type': abs_type,
                        'label': type_labels.get(abs_type, abs_type.capitalize())
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
    team = request.GET.get('team', 'all')
    absence_type = request.GET.get('type', 'all')

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    data = _get_planning_data(year, month, team=team, absence_type=absence_type)
    data.update({
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'selected_team': team,
        'selected_type': absence_type,
    })

    return render(request, "rh/planning_global.html", data)


@login_required
@user_passes_test(is_hr)
def export_planning_csv(request):
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    team = request.GET.get('team', 'all')
    absence_type = request.GET.get('type', 'all')

    data = _get_planning_data(year, month, team=team, absence_type=absence_type)

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
