from rest_framework import serializers
from .models import Mail

class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = ['id', 'subject', 'date_mail', 'sender_email_id']

class MailDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = '__all__'