from django.shortcuts import render
from rh.models import Conge, ficheDePaie
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
# Create your views here.
@login_required
def home_employee(request):
    return render(request, "employees/index.html")

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


@csrf_exempt
def annuler_conge(request, id):
    if request.method == "DELETE":
        conge = Conge.objects.get(id=id)
        conge.delete()
        return JsonResponse({"message": "Congé annulé"})
    

@login_required
def my_pay_slips(request):
    fiches = ficheDePaie.objects.filter(employee_profile__user=request.user).order_by('-year', '-month')
    
    return render(request, 'employees/my_fiches.html', {'fiches': fiches})

@login_required
def download_pay_slip(request, fiche_id):
    try:
        # On récupère la fiche ET on vérifie qu'elle appartient bien au user
        fiche = ficheDePaie.objects.get(id=fiche_id, employee_profile__user=request.user)
    except ficheDePaie.DoesNotExist:
        raise Http404("Fiche introuvable ou accès refusé")

    # On prépare la réponse pour forcer le téléchargement
    response = HttpResponse(fiche.pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Fiche_Paie_{fiche.month}_{fiche.year}.pdf"'
    
    return response

#switch de pages 
def absence(request):
    return render(request, "employees/absence.html")

def planning(request):
    return render(request, "employees/planning.html")
def fdp(request):
    return render(request, "employees/fdp.html")
