from django.db import models


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    title = models.CharField(max_length=30, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'employee'


class Mailadress(models.Model):
    mailadress_id = models.AutoField(primary_key=True)
    mail = models.CharField(max_length=200)
    employee = models.ForeignKey(Employee, models.DO_NOTHING, blank=True, null=True)
    mailadress_type = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mailadress'


class Mailbody(models.Model):
    mail_id = models.BigIntegerField(primary_key=True)
    sender = models.ForeignKey(Mailadress, models.DO_NOTHING, blank=True, null=True)
    mail_date = models.DateField(blank=True, null=True)
    mail_subject = models.TextField(blank=True, null=True)
    mail_content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mailbody'


class Mailheader(models.Model):
    mailheader_id = models.AutoField(primary_key=True)
    mail = models.ForeignKey(Mailbody, models.DO_NOTHING, blank=True, null=True)
    receiver = models.ForeignKey(Mailadress, models.DO_NOTHING)
    mailheader_type = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mailheader'
