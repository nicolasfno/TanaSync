from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_rh, name='home_rh'),
    path('equipe/', views.vue_equipe, name='vue_equipe'),
    path('validation-demandes/', views.validation_demandes, name='validation_demandes'),
    path('planning-global/', views.planning_global, name='planning_global'),
    path('absences/', views.absences_rh, name='absences_rh'),
    path('fiches-paie/', views.fiches_de_paie_rh, name='fiches_de_paie_rh'),
    path('planning/', views.planning_rh, name='planning_rh'),
    path('conges/', views.liste_conges, name='liste_conges'),
    path('conges/<int:employee_id>/', views.liste_conges_spe, name='liste_conges_spe'),
    path('conges/modifier/<int:id>/', views.modifier_conge, name='modifier_conge'),
]