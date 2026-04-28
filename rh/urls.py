from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_rh, name='home_rh'),
    path('equipe/', views.vue_equipe, name='vue_equipe'),
    path('validation-demandes/', views.validation_demandes, name='validation_demandes'),
    path('planning-global/', views.planning_global, name='planning_global'),
    path('planning-global/export/', views.export_planning_csv, name='export_planning_csv'),
    path('absences/', views.absences_rh, name='absences_rh'),
    path('absences/annuler/<int:id>/', views.rh_annuler_conge, name='rh_annuler_conge'),
    path('fiches-paie/', views.fiches_de_paie_rh, name='fiches_de_paie_rh'),
    path('planning/', views.planning_rh, name='planning_rh'),
    path('conges/', views.liste_conges, name='liste_conges'),
    path('conges/<int:employee_id>/', views.liste_conges_spe, name='liste_conges_spe'),
    path('conges/modifier/<int:id>/', views.modifier_conge, name='modifier_conge'),
    path('conges/traiter/<int:id>/', views.traiter_conge, name='traiter_conge'),
    # API Endpoints
    path('api/planning/<int:year>/<int:month>/', views.api_planning_global, name='api_planning_global'),
    path('api/employees/', views.api_employees, name='api_employees'),
    path('api/conges/pending/', views.api_conges_pending, name='api_conges_pending'),
    path('api/pay-slips/', views.list_pay_slips, name='api_pay_slips'),  # Déjà existe
]