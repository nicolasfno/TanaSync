from django.shortcuts import render

# Create your views here.
def home_employee(request):
    return render(request, "employees/index.html")