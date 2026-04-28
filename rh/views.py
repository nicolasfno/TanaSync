from django.shortcuts import render
from rh.models import Conge, ficheDePaie
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import create_file  # Assurez-vous d'avoir une fonction pour créer un PDF
from django.contrib.auth.decorators import login_required, user_passes_test






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
def planning_global(request):
    return render(request, "rh/planning_global.html")

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