from django.shortcuts import render, redirect
from django.urls import reverse
from rh.models import Conge, ficheDePaie
# Import des helpers centralisés dans rh.views pour éviter la duplication
from rh.views import _build_absences_context, _get_conge_type_label, MONTH_NAMES_FR
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
import calendar
from datetime import datetime


# Create your views here.
@login_required
def home_employee(request):
    profile = request.user.employee_profile
    ctx = _build_absences_context(profile, 'mes_demandes')

    activities = []
    for conge in ctx['conges'][:5]:
        if conge['status'] == 'Accepté':
            icon, css, text = '✅', 'green', 'Votre demande de congé a été approuvée'
        elif conge['status'] == 'Refusé':
            icon, css, text = '❌', 'red', 'Votre demande de congé a été refusée'
        else:
            icon, css, text = '⏳', 'yellow', 'Demande de congé soumise'
        activities.append({
            'icon': icon, 'icon_class': css, 'text': text,
            'date_label': conge['created_at'],
        })

    _mois_inverse = {v: k for k, v in MONTH_NAMES_FR.items()}
    prochaine_paie = None
    derniere_fiche = ficheDePaie.objects.filter(employee_profile=profile).order_by('-year', '-month').first()
    if derniere_fiche:
        try:
            month_num = int(derniere_fiche.month)
        except (ValueError, TypeError):
            month_num = _mois_inverse.get(derniere_fiche.month, 1)
        next_month = month_num % 12 + 1
        next_year = int(derniere_fiche.year) + (1 if month_num == 12 else 0)
        prochaine_paie = f"28 {MONTH_NAMES_FR[next_month]} {next_year}"

        activities.append({
            'icon': '📄', 'icon_class': 'rose',
            'text': f'Fiche de paie disponible — {derniere_fiche.month} {derniere_fiche.year}',
            'date_label': f'{derniere_fiche.month} {derniere_fiche.year}',
        })

    return render(request, "employees/index.html", {
        'jours_restants': ctx['jours_restants'],
        'prochaine_paie': prochaine_paie,
        'activities': activities,
    })


def liste_conges(request):
    if request.method == 'GET':
        conges = Conge.objects.filter(employee_profile__user=request.user)
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
def demander_conge(request):
    """Endpoint JSON conservé pour compatibilité API existante."""
    if request.method == "POST":
        data = json.loads(request.body)
        conge = Conge.objects.create(
            employee_profile_id=data["employee_profile_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            reason=data.get("reason", "")
        )
        return JsonResponse({"message": "Congé demandé", "id": conge.id})
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


@login_required
def annuler_conge(request, id):
    """
    Annule (supprime) un congé appartenant à l'utilisateur connecté.
    Accepte POST (form HTML) et DELETE (API JSON) pour rester compatible
    avec l'ancien endpoint tout en supportant les formulaires.
    """
    if request.method in ("DELETE", "POST"):
        try:
            conge = Conge.objects.get(id=id, employee_profile__user=request.user)
            conge.delete()
        except Conge.DoesNotExist:
            pass
        if request.method == "DELETE":
            return JsonResponse({"message": "Congé annulé"})
        return redirect(reverse('mes_absences') + '?tab=mes_demandes')
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


@login_required
def mes_absences(request):
    """
    Page principale de gestion des absences côté employé.
    Gère GET (affichage) et POST (soumission d'une nouvelle demande).
    La logique de données est déléguée à rh.views._build_absences_context
    pour éviter tout doublon avec la page absences RH.
    """
    profile = request.user.employee_profile
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
        return redirect(reverse('mes_absences') + '?tab=mes_demandes')

    context = _build_absences_context(profile, tab)
    context['cancel_url_name'] = 'annuler_conge'
    return render(request, "employees/absence.html", context)


@login_required
def my_pay_slips(request):
    fiches = ficheDePaie.objects.filter(employee_profile__user=request.user).order_by('-year', '-month')
    return render(request, 'employees/my_fiches.html', {'fiches': fiches})


@login_required
def download_pay_slip(request, fiche_id):
    try:
        fiche = ficheDePaie.objects.get(id=fiche_id, employee_profile__user=request.user)
    except ficheDePaie.DoesNotExist:
        raise Http404("Fiche introuvable ou accès refusé")
    response = HttpResponse(fiche.pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Fiche_Paie_{fiche.month}_{fiche.year}.pdf"'
    return response


def planning(request):
    return render(request, "employees/planning.html")


def fdp(request):
    return render(request, "employees/fdp.html")


def calendar_view(request):
    today = datetime.now()
    curr_year = datetime.now()
    curr_month = 4
    cal = calendar.Calendar(firtsweekday=6)
    monts_days = cal.monthdayscalendar(curr_year, curr_month)
    context = {
        'monts_days': monts_days,
        'current_day': 16,
        'month_name': "Avril 2026",
    }
    return render(request, 'calendar.html', context)
