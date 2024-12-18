from django.db import models


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'Employee'


class Email(models.Model):
    id = models.AutoField(primary_key=True)
    adrmail = models.CharField(max_length=255)
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True, db_column="employee_id")

    class Meta:
        db_table = 'Email'


class Mail(models.Model):
    mail_id = models.CharField(primary_key=True, unique=True, max_length=500)
    filepath = models.CharField(max_length=100)
    objet = models.CharField(max_length=300)
    date_mail = models.DateTimeField()
    message = models.TextField()
    is_reply = models.BooleanField()
    main_message = models.TextField()
    date_main_message = models.DateTimeField()
    email_address_id = models.ForeignKey(Email, on_delete=models.CASCADE, db_column="email_address_id")

    class Meta:
        db_table = 'Mail'


class Receiver(models.Model):
    id = models.AutoField(primary_key=True)
    genre = models.CharField(max_length=10)
    email_address_id = models.ForeignKey(Email, on_delete=models.CASCADE, db_column="email_address_id")
    mail_identifiant = models.ForeignKey(Mail, on_delete=models.CASCADE, db_column="mail_identifiant")

    class Meta:
        db_table = 'Receiver'