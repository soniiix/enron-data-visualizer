from django.core.management.base import BaseCommand
from base_app.models import Employee, Mail, Email
from base_app.models import Employee, Mail, Email
from base_project.settings import BASE_DIR
import xml.etree.ElementTree as xml
import os
import re
from django.db import transaction, IntegrityError
from datetime import datetime

class Command(BaseCommand):
    help = 'Enron - Script de peuplement'
    # Constantes pour les chemins de fichier
    DATA_DIR = BASE_DIR.parent / "data"
    EMPLOYEES_FILE = DATA_DIR / "employees.xml"
    MAIL_DIR = DATA_DIR / "maildir"

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            help="Permet de spécifier que l'on veut lancer le script sur un seul dossier."
        )

    def handle(self, *args, **options):
        # Phase de test
        self.stdout.write("----- Suppression des données précédentes -----")    
        self.deleteAll()

        self.stdout.write()
        self.stdout.write("----- Début du script -----")

        # Insertion en BDD des employés du fichier XML
        self.stdout.write("-- Traitement de employees.xml --")
        self.populateEmployees()

        # Insertion en BDD des mails
        self.startPopulateMails(options)

        self.stdout.write("----- Fin du script -----")
        


    def populateEmployees(self):
        """
        Fonction permettant de lire le contenu du fichier employees.xml,
        et de créer un Employé en BDD pour chaque enfant XML.
        """
        try:
            # Récupérer le contenu du fichier XML
            root = xml.parse(self.EMPLOYEES_FILE).getroot()

            # Définir des compteurs pour vérifier la cohérence
            initial_emp_count = 0
            inserted_emp_count = 0

            # Définir des compteurs pour vérifier la cohérence
            initial_emp_count = 0
            inserted_emp_count = 0

            # Parcourir les éléments du fichier
            for child in root:
                # Incrémenter le compteur
                initial_emp_count += 1

                # Incrémenter le compteur
                initial_emp_count += 1

                # Récupérer la catégorie de l'employé si celle-ci est définie
                category = child.attrib['category'] if (child.attrib != {}) else None

                emails = []
                # Récupérer le reste des informations de l'employé (nom, prénom, liste des emails, nom de la boîte mail)
                for subchild in child:
                    match subchild.tag:
                        case "firstname":
                            firstname = subchild.text
                        case "lastname":
                            lastname = subchild.text
                        case "email":
                            emails.append(subchild.attrib['address'])
                        case "mailbox":
                            mailbox = subchild.text

                # Créer une instance Employee et l'enregistrer dans la base
                try:
                    new_emp = Employee(firstname=firstname, lastname=lastname, category=category)
                    new_emp.save()
                    inserted_emp_count += 1
                    
                    # Gérer la liste des emails de l'employé (+mailbox?)
                    for email in emails:
                        new_email = Email(adrmail=email, employee_id=new_emp)
                        new_email.save()
                except Exception as e:
                    print(f"Erreur lors de l'insertion de l'employé : {e}")

            # Affichage des statuts
            print("Données enregistrées.")
            print(f"Nombre d'employés initial: {initial_emp_count}")
            print(f"Nombre d'employés insérés: {inserted_emp_count}")
        except Exception as e:
            print(f"Erreur lors de l'exécution: {str(e)}")


    def startPopulateMails(self, options):
        total_files = 0
        processed_files = 0
        skipped_files = 0

        folder_to_process = options['folder']
        if folder_to_process:
            folder_path = os.path.join(self.MAIL_DIR, folder_to_process)
            if os.path.isdir(folder_path):
                self.stdout.write(f"Processing single folder: {folder_path}")
                stats = self.populateMails(folder_path)
                total_files += stats['total_files']
                processed_files += stats['processed_files']
                skipped_files += stats['skipped_files']
            else:
                self.stdout.write(f"Specified folder '{folder_to_process}' not found.")
                return
        else:
            for folder in os.listdir(self.MAIL_DIR):
                folder_path = os.path.join(self.MAIL_DIR, folder)
                if os.path.isdir(folder_path):
                    self.stdout.write(f"Processing folder: {folder_path}")
                    stats = self.populateMails(folder_path)
                    total_files += stats['total_files']
                    processed_files += stats['processed_files']
                    skipped_files += stats['skipped_files']

        print("--- Statistiques finales ---")
        print(f"Nombre de fichiers total: {total_files}")
        print(f"Fichiers traités: {processed_files}")
        print(f"Fichiers ignorés (en-tête manquant): {skipped_files}")


    def populateMails(self, folder_path):
        mail_objects = []
        email_cache = {}
        total_files = 0
        processed_files = 0
        skipped_files = 0

        existing_ids = set(Mail.objects.values_list('mail_id', flat=True))

        for root, _, files in os.walk(folder_path):
            for file_name in files:
                total_files += 1
                file_path = os.path.join(root, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()

                        headers = self.extract_mail_headers(content)
                        if not headers.get('message_id') or not headers.get('date'):
                            skipped_files += 1
                            continue

                        message_id = headers['message_id'][:255]

                        date_mail = self.extractDate(headers['date'])
                        if not date_mail:
                            # Si la date n'est pas parsée correctement, on saute
                            skipped_files += 1
                            continue

                        email_address = headers.get('from')
                        if email_address:
                            email_obj = self.getEmailObj(email_address, email_cache)
                        else:
                            skipped_files += 1
                            continue

                        first_message_date = self.findFirstMessageDate(content)
                        # Si aucune date pour le premier message, on peut réutiliser date_mail
                        if not first_message_date:
                            first_message_date = date_mail

                        objet = headers.get('subject', '')[:255]
                        main_message = None
                        if objet and "Re:" in objet:
                            main_message = self.extractFirstMessageOnly(content)
                        if main_message is None:
                            main_message = ""

                        # Normalisation du chemin
                        relative_path = os.path.relpath(file_path, self.MAIL_DIR)
                        relative_path = relative_path.replace(os.path.sep, '/')

                        mail_objects.append(Mail(
                            mail_id=message_id,
                            filepath=relative_path,
                            objet=objet,
                            date_mail=date_mail,  # datetime object
                            message=self.extractMessageBody(content),
                            is_reply=True if objet and "Re:" in objet else False,
                            main_message=main_message,
                            date_main_message=first_message_date,  # datetime object
                            email_address_id=email_obj  # ForeignKey: passer l'objet directement
                        ))
                        processed_files += 1
                except Exception as e:
                    self.stdout.write(f"Error processing file {file_path}: {str(e)}")

        try:
            with transaction.atomic():
                Mail.objects.bulk_create(mail_objects, batch_size=1000)
                self.stdout.write(f"Inserted {len(mail_objects)} mails into the database.")
        except IntegrityError as e:
            self.stdout.write(f"Database error: {e}")

        return {
            'total_files': total_files,
            'processed_files': processed_files,
            'skipped_files': skipped_files
        }


    def extract_mail_headers(self, content):
        headers = {}
        headers['message_id'] = self.safeExtract(r'^Message-ID: (.+)', content)
        headers['date'] = self.safeExtract(r'^Date: (.+)', content)
        headers['from'] = self.safeExtract(r'^From: (.+)', content)
        headers['subject'] = self.safeExtract(r'^Subject: (.*)', content)
        return headers


    def safeExtract(self, pattern, content):
        match_obj = re.search(pattern, content, re.MULTILINE)
        return match_obj.group(1).strip() if match_obj else None


    def extractDate(self, raw_date):
        """
        Retourne un objet datetime ou None
        """
        try:
            clean_date = re.sub(r'\s*\([^)]*\)', '', raw_date)
            # Retourne directement un datetime
            return datetime.strptime(clean_date, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            return None


    def extractMessageBody(self, content):
        match_obj = re.search(r'\n\n(.*)', content, re.DOTALL)
        if match_obj:
            return match_obj.group(1).strip()
        return ""


    def extractFirstMessageOnly(self, content):
        parts = content.split("\n\n", 1)
        if len(parts) < 2:
            return ""

        body = parts[1]
        body_cleaned = re.split(r'\nFrom: |\n-{2,} Forwarded by', body, maxsplit=1)[0]
        return body_cleaned.strip()


    def findFirstMessageDate(self, content):
        """
        Retourne un datetime du premier message, ou None si aucune date n'est trouvée.
        """
        message_blocks = re.split(r'(-{2,} Forwarded by .*? -{2,})|(From: .+)', content, flags=re.DOTALL)
        dates = []

        for block in message_blocks:
            if block:
                match_obj = re.search(r'^Date: (.+)', block, re.MULTILINE)
                if match_obj:
                    raw_date = match_obj.group(1)
                    clean_date = re.sub(r'\s*\([^)]*\)', '', raw_date)
                    try:
                        parsed_date = datetime.strptime(clean_date, "%a, %d %b %Y %H:%M:%S %z")
                        dates.append(parsed_date)
                    except ValueError:
                        continue

        return min(dates) if dates else None


    def getEmailObj(self, from_email, email_cache):
        if from_email in email_cache:
            return email_cache[from_email]

        email_obj = Email.objects.filter(adrmail=from_email).first()
        if not email_obj:
            external_employee = Employee.objects.create(
                firstname="Personne",
                lastname="Externe",
                category="Externe"
            )
            email_obj = Email.objects.create(
                adrmail=from_email,
                employee_id=external_employee
            )

        email_cache[from_email] = email_obj
        return email_obj


    def deleteAll(self):
        try:
            Mail.objects.all().delete()
            Email.objects.all().delete()
            Employee.objects.all().delete()
            print("Toutes les données ont été supprimées.")
        except Exception as e:
            print(f"Erreur lors de la suppression : {str(e)}")
