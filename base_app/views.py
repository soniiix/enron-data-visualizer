import json
from django.shortcuts import render
from base_app.models import Mail, Employee, Email
from datetime import datetime
from django.db.models import Count
import re
from collections import Counter
from base_app.utils import getExcludedWords
from django.db.models.functions import TruncMonth
import locale
from django.core.exceptions import ObjectDoesNotExist

# Définir la locale en français pour afficher les mois en français
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "fr_FR")  # Option alternative si UTF-8 ne fonctionne pas

def home(request):
    try:
        CURRENT_YEAR = datetime.today().year
        YEARS_RANGE = ["1900", CURRENT_YEAR]
        EXCLUDED_WORDS = getExcludedWords()
    
        # Nombre total de mails
        email_count = Mail.objects.count()

        # Nombre total de personnes
        people_count = Employee.objects.count()
        
        # Récupérer la période couverte
        min_year = Mail.objects.filter(date_mail__year__range=YEARS_RANGE).earliest("date_mail").date_mail.year
        max_year = Mail.objects.filter(date_mail__year__range=YEARS_RANGE).latest("date_mail").date_mail.year
        covered_period = f"{min_year} - {max_year}"

        # Récupérer l'année sélectionnée dans le graphique (par défaut, l'année maximale en BDD)
        selected_year = int(request.GET.get('year', max_year))

        # Faire une liste décroissante de chaque année de la période couverte pour la select box
        years_list = list(range(max_year, min_year-1, -1))

        # Trouver les 3 personnes les plus actives (en fonction du nombre de mails envoyés)
        top3_employee = (Employee.objects.annotate(email_count=Count('email__mail')).order_by('-email_count')[:3])
        top3_people = []
        # Récupérer l'email le plus utilisé de chaque employé
        for employee in top3_employee:
            email = (
                Email.objects.filter(employee_id=employee)
                .annotate(email_count=Count('mail'))
                .order_by('-email_count')
                .first()
            )
            top3_people.append(
                {
                    "person": employee,
                    "email_address": email.email_address
                }
            )

        # Trouver les 3 mots les plus récurrents
        all_messages = Mail.objects.values_list("message", flat=True)  # Récupérer le message de chaque mail
        global_word_counts = Counter()  # Compteur global pour tous les mots
        for message in all_messages:
            words = re.findall(r'\b[A-Za-z]+\b', message)  # Récupérer uniquement les mots
            words = [word for word in words if word.lower() not in EXCLUDED_WORDS]  # Exclure les mots inutiles
            global_word_counts.update(words)  # Ajouter les occurrences des mots de ce message au compteur global
        top3_words = [{"word": word, "count": count} for word, count in global_word_counts.most_common(3)]  # Obtenir les 3 mots les plus fréquents

        # Récupérer le nombre de mails envoyés par mois pour l'année choisie dans le graphique
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

        # Filtrer les employés internes
        internal_employees = Employee.objects.exclude(category='Externe')

        # Trouver les emails envoyés par des employés internes à des externes
        sent_to_externals = Mail.objects.filter(
            sender_email_id__employee_id__in=internal_employees,
            receiver__email_address_id__employee_id__category='Externe'
        )

        # Trouver les emails reçus par des employés internes d'externes
        received_from_externals = Mail.objects.filter(
            receiver__email_address_id__employee_id__in=internal_employees,
            sender_email_id__employee_id__category='Externe'
        )

        # Combiner les deux sets de mails
        all_interactions = sent_to_externals | received_from_externals

        # Compter les interactions pour chaque employé
        employee_interactions = all_interactions.values('sender_email_id__employee_id').annotate(
            interactions_count=Count('id')
        ).order_by('-interactions_count')[:3]

        # Calculer le total des échanges
        total_interactions = all_interactions.count()

        # Passer les 3 employés ayant le plus d'échanges au template
        employees_with_most_exchanges = []
        for interaction in employee_interactions:
            employee = Employee.objects.get(id=interaction['sender_email_id__employee_id'])
            interactions_count = interaction['interactions_count']
            
            # Calcul du pourcentage
            if total_interactions > 0:
                percentage = (interactions_count / total_interactions) * 100
            else:
                percentage = 0

            employees_with_most_exchanges.append({
                'firstname': employee.firstname,
                'lastname': employee.lastname,
                'category': employee.category,
                'interactions_count': interaction['interactions_count'],
                'percentage': round(percentage, 2)
            })

        context = {
            "error": False,
            "email_count": format(email_count, ',').replace(',', ' '),
            "people_count": format(people_count, ',').replace(',', ' '),
            "covered_period": covered_period,
            "top3_people": top3_people,
            "top3_words": top3_words,
            "years_list": years_list,
            "selected_year": selected_year,  # Année choisie dans le graphique
            "mail_data": mail_data,  # Données pour le graphique
            "employees_with_most_exchanges": employees_with_most_exchanges
        }
        
        return render(request, "home.html", context)
    except ObjectDoesNotExist:
        context = {
            "error": True
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
    employees = Employee.objects.all().values('id', 'firstname', 'lastname', 'category')
    # Sérialiser manuellement les données en JSON
    employees_json = json.dumps(list(employees))

    context = {
        'employees_json': employees_json,
    }

    return render(request, "favorites.html", context)
