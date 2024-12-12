from django.db import models


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=45)
    lastname = models.CharField(max_length=45)
    category = models.CharField(max_length=45, blank=True, null=True)
    
    class Meta:
        db_table = 'Employee'


class Email(models.Model):
    id = models.AutoField(primary_key=True)
    adrmail = models.CharField(max_length=45)
    employee_id = models.ForeignKey(Employee, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Email'


class Mail(models.Model):
    mail_id = models.CharField(primary_key=True, unique=True)
    filepath = models.CharField(max_length=45)
    objet = models.CharField(max_length=45)
    date_mail = models.DateTimeField()
    message = models.TextField()
    is_reply = models.BooleanField()
    main_message = models.TextField()
    date_main_message = models.DateTimeField()
    email_address_id = models.ForeignKey(Email, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Mail'


class Receiver(models.Model):
    id = models.AutoField(primary_key=True)
    genre = models.CharField(max_length=10)
    email_address_id = models.ForeignKey(Email, on_delete=models.CASCADE)
    mail_identifiant = models.ForeignKey(Mail, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Receiver'