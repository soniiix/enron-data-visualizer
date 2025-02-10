from django.shortcuts import render
from base_app.models import Mail, Employee, Email
from datetime import datetime
from django.db.models import Count
import re
from collections import Counter
from base_app.useful_functions import getExcludedWords
from django.db.models.functions import TruncMonth
import locale

# Définir la locale en français pour afficher les mois en français
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "fr_FR")  # Option alternative si UTF-8 ne fonctionne pas

def home(request):
    CURRENT_YEAR = datetime.today().year
    YEARS_RANGE = ["1900", CURRENT_YEAR]
    EXCLUDED_WORDS = getExcludedWords()

    # Récupérer l'année sélectionnée (par défaut, l'année en cours)
    selected_year = int(request.GET.get('year', CURRENT_YEAR))
    
    # Nombre total de mails
    email_count = Mail.objects.count()

    # Nombre total de personnes
    people_count = Employee.objects.count()
    
    # Récupérer la période couverte
    min_year = Mail.objects.filter(date_mail__year__range=YEARS_RANGE).earliest("date_mail").date_mail.year
    max_year = Mail.objects.filter(date_mail__year__range=YEARS_RANGE).latest("date_mail").date_mail.year
    covered_period = f"{min_year} - {max_year}"

    # Faire une liste décroissante de chaque année de la période couverte pour la select box
    years_list = list(range(max_year, min_year-1, -1))

    # Trouver les 3 personnes les plus actives (en fonction du nombre de mails envoyés)
    top3_people = (Employee.objects.annotate(email_count=Count('email__mail')).order_by('-email_count')[:3])

    # Trouver les 3 mots les plus récurrents
    all_messages = Mail.objects.values_list("message", flat=True)  # Récupérer le message de chaque mail
    global_word_counts = Counter()  # Compteur global pour tous les mots
    for message in all_messages:
        words = re.findall(r'\b[A-Za-z]+\b', message)  # Récupérer uniquement les mots
        words = [word for word in words if word.lower() not in EXCLUDED_WORDS]  # Exclure les mots inutiles
        global_word_counts.update(words)  # Ajouter les occurrences des mots de ce message au compteur global
    top3_words = [{"word": word, "count": count} for word, count in global_word_counts.most_common(3)]  # Obtenir les 3 mots les plus fréquents

    # Récupérer le nombre de mails envoyés par mois pour l'année choisie
    mail_per_month = (
        Mail.objects.filter(date_mail__year=selected_year)
        .annotate(month=TruncMonth('date_mail'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Préparer les données pour le graphique avec les mois en français
    mail_data = {
        "labels": [m["month"].strftime("%B").capitalize() for m in mail_per_month],  # Mois en français
        "values": [m["count"] for m in mail_per_month],  # Nombre de mails par mois
    }

    context = {
        "email_count": format(email_count, ',').replace(',', ' '),
        "people_count": format(people_count, ',').replace(',', ' '),
        "covered_period": covered_period,
        "top3_people": top3_people,
        "top3_words": top3_words,
        "years_list": years_list,
        "selected_year": selected_year,  # Année choisie
        "mail_data": mail_data,  # Données pour le graphique
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
