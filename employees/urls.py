from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_employee, name='home_employee'),
    path('conges/', views.liste_conges, name='liste_conges_employee'),
    path('demander/', views.demander_conge, name='demander_conge'),
    path('annuler/<int:id>/', views.annuler_conge, name='annuler_conge'),
    path('mes-fiches/', views.my_pay_slips, name='my_pay_slips'),
    path('telecharger-fiche/<int:fiche_id>/', views.download_pay_slip, name='download_pay_slip'),
    path('planning/', views.planning, name='planning'),
    path('absences/', views.mes_absences, name='mes_absences'),
    path('fdp/', views.fdp, name='fdp'),
]
