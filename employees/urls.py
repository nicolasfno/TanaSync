from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_employee, name='home_employee'),
    path('conges/', views.liste_conges, name='liste_conges'),
    path('demander/', views.demander_conge, name='demander_conge'),
    path('annuler/<int:id>/', views.annuler_conge, name='annuler_conge'),
]