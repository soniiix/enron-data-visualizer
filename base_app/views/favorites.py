import json
from django.shortcuts import render
from base_app.models import Employee

def favorites(request):
    employees = Employee.objects.all().values('id', 'firstname', 'lastname', 'category')
    # Sérialiser manuellement les données en JSON
    employees_json = json.dumps(list(employees))

    context = {
        'employees_json': employees_json,
    }

    return render(request, "favorites.html", context)