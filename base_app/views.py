import json
from django.shortcuts import render
from base_app.models import Mail, Employee, Email
from datetime import datetime
from django.db.models import Count, Avg, Q
from django.db.models.functions import (
    TruncMonth, TruncHour, TruncDate, TruncYear, TruncDay,
    Extract, ExtractWeekDay, ExtractHour, Length
)
from rest_framework.views import APIView
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from base_app.serializers import MailSerializer, MailDetailSerializer
from rest_framework.response import Response
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

def statistics(request):
    # Répartition par dossier
    folders = Mail.objects.values_list('filepath', flat=True)
    folder_counts = {}
    for path in folders:
        if '/' in path:
            folder = path.split('/')[1]
            folder_counts[folder] = folder_counts.get(folder, 0) + 1

    # Configuration granularité
    granularity = request.GET.get('granularity', 'day')

    # Données Originaux/Réponses
    response_data = {
        "labels": ["Originaux", "Réponses"],
        "values": [
            Mail.objects.filter(is_reply=False).count(),
            Mail.objects.filter(is_reply=True).count()
        ]
    }

    # Gestion requête AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return handle_ajax_request(request)

    # Données temporelles
    qs, date_format = build_queryset(request, granularity)
    line_data = format_line_data(qs, granularity, date_format)

    # Activité des expéditeurs
    sender_data = get_sender_activity_data()

    # Analyse de la longueur des messages et des sujets
    def get_avg_length(queryset, field):
        result = queryset.aggregate(avg_length=Avg(Length(field)))['avg_length']
        return float(result) if result is not None else 0.0

    length_data = {
        "labels": ["Originaux - Sujet", "Réponses - Sujet", "Originaux - Message", "Réponses - Message"],
        "values": [
            get_avg_length(Mail.objects.filter(is_reply=False), 'subject'),
            get_avg_length(Mail.objects.filter(is_reply=True), 'subject'),
            get_avg_length(Mail.objects.filter(is_reply=False), 'message'),
            get_avg_length(Mail.objects.filter(is_reply=True), 'message')
        ]
    }

    return render(request, 'statistiques.html', {
        "folder_data": json.dumps({
            "labels": list(folder_counts.keys()),
            "values": list(folder_counts.values())
        }),
        "line_data": json.dumps(line_data),
        "response_data": json.dumps(response_data),
        "sender_data": json.dumps(sender_data),
        "length_data": json.dumps(length_data),  # Ajout de length_data au contexte
    })


def get_sender_activity_data(limit=10):
    # Récupère les expéditeurs via la relation Email
    senders = (Mail.objects
               .exclude(sender_email_id__isnull=True)
               .values('sender_email_id__email_address')
               .annotate(count=Count('id'))
               .order_by('-count')[:limit])

    if not senders:
        return {"labels": ["Aucun expéditeur"], "values": [0]}

    return {
        "labels": [s['sender_email_id__email_address'] for s in senders],
        "values": [s['count'] for s in senders]
    }


def handle_ajax_request(request):
    """Gère les requêtes AJAX pour le graphique d'évolution"""
    granularity = request.GET.get('granularity', 'day')
    qs, date_format = build_queryset(request, granularity)
    line_data = format_line_data(qs, granularity, date_format)
    return JsonResponse(line_data)


def build_queryset(request, granularity):
    """Construit le queryset pour le graphique temporel"""
    trunc_mapping = {
        'hour': (TruncHour('date_mail'), "%Y-%m-%d %H:%M"),
        'day': (TruncDay('date_mail'), "%Y-%m-%d"),
        'month': (TruncMonth('date_mail'), "%Y-%m"),
        'year': (TruncYear('date_mail'), "%Y"),
        'range': (TruncDay('date_mail'), "%Y-%m-%d")
    }

    trunc_func, date_format = trunc_mapping.get(
        granularity,
        (TruncDay('date_mail'), "%Y-%m-%d")
    )

    qs = Mail.objects.all()

    if granularity == 'range':
        try:
            start_date = datetime.strptime(
                request.GET.get('start_date', '1980-01-01'),
                "%Y-%m-%d"
            )
            end_date = datetime.strptime(
                request.GET.get('end_date', '2002-12-31'),
                "%Y-%m-%d"
            )
            qs = qs.filter(date_mail__date__range=(start_date.date(), end_date.date()))
        except ValueError:
            pass

    return (qs.annotate(period=trunc_func)
              .values('period')
              .annotate(count=Count('id'))
              .order_by('period'), date_format)


def format_line_data(queryset, granularity, date_format):
    """Formate les données pour le graphique linéaire"""
    return {
        "labels": [entry['period'].strftime(date_format) for entry in queryset],
        "values": [entry['count'] for entry in queryset]
    }


class EmailListAPIView(APIView):
    def get(self, request, format=None):
        # Get search parameters
        search_type = request.query_params.get('type', 'all')
        query = request.query_params.get('query', '')
        start_date = request.query_params.get('startDate')
        end_date = request.query_params.get('endDate')
        last_date_str = request.query_params.get('lastDate')

        # Start with all emails
        emails = Mail.objects.all()

        # Apply date filter if searching by date
        if search_type == 'date' and start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            emails = emails.filter(date_mail__range=(start_date, end_date))
        elif query:
            # Apply text search based on search type
            if search_type == 'all':
                emails = emails.filter(
                    Q(id__icontains=query) |
                    Q(filepath__icontains=query) |
                    Q(subject__icontains=query) |
                    Q(message__icontains=query)
                )
            elif search_type in ['id', 'filepath', 'subject', 'message']:
                emails = emails.filter(**{f"{search_type}__icontains": query})

        # Apply pagination (lazy load)
        if last_date_str:
            last_date = parse_datetime(last_date_str)
            if last_date:
                emails = emails.filter(date_mail__lt=last_date)

        # Order and limit results
        emails = emails.order_by('-date_mail')[:50]

        serializer = MailSerializer(emails, many=True)
        return Response(serializer.data)


class EmailDetailAPIView(APIView):
    def get(self, request, id, format=None):
        email = get_email_by_id(id)
        if not email:
            return Response({'error': 'Email non trouvé.'}, status=404)
        serializer = MailDetailSerializer(email)
        return Response(serializer.data)


def get_email_by_id(raw_id):
    cleaned = raw_id.strip()
    if not (cleaned.startswith("<") and cleaned.endswith(">")):
        cleaned = f"<{cleaned}>"
    return Mail.objects.filter(pk__iexact=cleaned).first()


def mails(request):
    return render(request, "mails.html")