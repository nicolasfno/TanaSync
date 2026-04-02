from django.urls import path
from . import views

urlpatterns = [
    path('conges/', views.liste_conges, name='liste_conges'),
    path('conges/<int:employee_id>/', views.liste_conges_spe, name='liste_conges_spe'),
    path('conges/modifier/<int:id>/', views.modifier_conge, name='modifier_conge'),
]