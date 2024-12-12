from django.contrib import admin

# Register your models here.
from .models import Employee, Email, Mail, Receiver

admin.site.register(Employee)
admin.site.register(Email)
admin.site.register(Mail)
admin.site.register(Receiver)