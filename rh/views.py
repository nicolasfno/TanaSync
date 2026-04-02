from django.shortcuts import render
from rh.models import Conge, ficheDePaie
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
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
