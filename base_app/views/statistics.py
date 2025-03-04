from django.shortcuts import render
import json
from base_app.models import Mail
from datetime import datetime
from rest_framework.views import APIView
from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncHour, TruncYear, TruncDay, Length
from rest_framework.response import Response
from base_app.serializers import MailSerializer, MailDetailSerializer
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

def statistics(request):
    if Mail.objects.count() == 0:
        context = {
            "error": True
        }
        return render(request, "statistics.html", context)


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

    return render(request, 'statistics.html', {
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
