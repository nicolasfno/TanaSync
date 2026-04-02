from django.shortcuts import render
from rh.models import Conge, ficheDePaie
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
def home_employee(request):
    return render(request, "employees/index.html")

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
    
@csrf_exempt
def demander_conge(request):
    if request.method == "POST":
        data = json.loads(request.body)
        conge = Conge.objects.create(
            employee_id=data["employee_id"],
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
    
