from django.shortcuts import render
from base_app.models import Mail, Employee, Email
from datetime import datetime
from django.db.models import Count

def home(request):
    CURRENT_YEAR = datetime.today().year
    YEARS_RANGE = ["1900", CURRENT_YEAR]
    
    # Nombre total de mails
    email_count = Mail.objects.count()
    # Nombre total de personnes?
    people_count = Employee.objects.count()
    # Récupérer la période couverte
    min_year = Mail.objects.filter(date_mail__year__range=YEARS_RANGE).earliest("date_mail").date_mail.year
    max_year = Mail.objects.filter(date_mail__year__range=YEARS_RANGE).latest("date_mail").date_mail.year
    covered_period = f"{min_year} - {max_year}"
    # Trouver les 3 personnes les plus actives (en fonction du nombre de mails envoyés)
    top3_people = (Employee.objects.annotate(email_count=Count('email__mail')).order_by('-email_count')[:3])

    context = {
        "email_count": format(email_count, ',').replace(',', ' '),
        "people_count": format(people_count, ',').replace(',', ' '),
        "covered_period": covered_period,
        "top3_people": top3_people
    }
    return render(request, "home.html", context)

def people(request):
    return render(request, "people.html")

def mails(request):
    return render(request, "mails.html")

def favorites(request):
    return render(request, "favorites.html")