from django.shortcuts import render
from base_app.models import Mail, Employee, Email
from datetime import datetime
from django.db.models import Count
import re
from collections import Counter
from base_app.useful_functions import getExcludedWords

def home(request):
    CURRENT_YEAR = datetime.today().year
    YEARS_RANGE = ["1900", CURRENT_YEAR]
    EXCLUDED_WORDS = getExcludedWords()
    
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

    # Trouver les 3 mots les plus récurrents
    all_messages = Mail.objects.values_list("message", flat=True) # Récupérer le message de chaque mail
    global_word_counts = Counter() # Compteur global pour tous les mots
    for message in all_messages:
        words = re.findall(r'\b[A-Za-z]+\b', message) # Récupérer uniquement les mots
        words = [word for word in words if word.lower() not in EXCLUDED_WORDS] # Exclure les mots qui ne sont pas des vrais mots
        global_word_counts.update(words) # Ajouter les occurrences des mots de ce message au compteur global
    top3_words = [{"word": word, "count": count} for word, count in global_word_counts.most_common(3)] # Obtenir les 3 mots les plus fréquents

    context = {
        "email_count": format(email_count, ',').replace(',', ' '),
        "people_count": format(people_count, ',').replace(',', ' '),
        "covered_period": covered_period,
        "top3_people": top3_people,
        "top3_words": top3_words
    }
    return render(request, "home.html", context)


def people(request):
    category_filter = request.GET.get('category', None)

    if category_filter:
        employees = Employee.objects.filter(category=category_filter)
    else:
        employees = Employee.objects.all()
        
    categories = Employee.objects.values_list('category', flat=True).distinct()

    context = {
        'employees': employees,
        'categories': categories,
    }

    return render(request, 'people.html', context)


def mails(request):
    return render(request, "mails.html")


def favorites(request):
    return render(request, "favorites.html")