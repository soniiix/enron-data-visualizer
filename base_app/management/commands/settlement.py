from django.core.management.base import BaseCommand
from base_app.models import Employee, Mail, Email, Receiver
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

    # Codes ANSI pour la stylisation de la console
    COLORS = {
        "PURPLE": "\033[95m",   # Violet clair
        "CYAN": "\033[36m",     # Cyan
        "OK": "\033[92m",       # Vert
        "ERROR": "\033[91m",    # Rouge
        "END_STYLE": "\033[0m", # Réinitialisation
    }

    def stylize(self, text: str, color: str) -> str:
        """
        Applique un style de couleur ANSI à une chaîne de texte.

        Options disponibles : PURPLE, CYAN, OK, ERROR, END_STYLE.
        """
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['END_STYLE']}"


    def add_arguments(self, parser):
        """
        Ajoute des arguments supplémentaires à la commande Django.
        """
        parser.add_argument(
            '--folder',
            type=str,
            help="Permet de spécifier que l'on veut lancer le script sur un seul dossier."
        )


    def handle(self, *args, **options):
        """
        Méthode principale exécutée lorsqu'on lance la commande Django.
        """
        self.stdout.write()
        # Phase de test
        self.stdout.write(self.stylize("SUPPRESSION DES DONNÉES PRÉCÉDENTES", "CYAN"))
        self.deleteAll()

        self.stdout.write()

        # Insertion en BDD des employés du fichier XML
        self.stdout.write(self.stylize("PEUPLEMENT DES EMPLOYÉS", "CYAN"))
        self.stdout.write(f"Traitement de {self.stylize("employees.xml", "PURPLE")}...")
        self.populateEmployees()

        self.stdout.write()

        # Insertion en BDD des mails
        self.stdout.write(self.stylize("PEUPLEMENT DES MAILS", "CYAN"))
        self.startPopulateMails(options)
        

    def populateEmployees(self):
        """
        Lit le fichier employees.xml et insère les employés dans la base de données.

        Traite chaque élément XML pour créer des enregistrements Employee et Email associés.
        """
        try:
            # Récupérer le contenu du fichier XML
            root = xml.parse(self.EMPLOYEES_FILE).getroot()

            # Définir des compteurs pour vérifier la cohérence
            initial_emp_count = 0
            inserted_emp_count = 0

            # Parcourir les éléments du fichier
            for child in root:
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
                        new_email = Email(email_address=email, employee_id=new_emp)
                        new_email.save()
                except Exception as e:
                    print(f"{self.stylize("Erreur lors de l'insertion de l'employé :", "ERROR")} {e}")

            # Affichage des statuts
            print(self.stylize(f"{inserted_emp_count}/{initial_emp_count} employés insérés dans la base de données.", "OK"))
        except Exception as e:
            print(f"Erreur lors de l'exécution: {str(e)}")


    def startPopulateMails(self, options):
        """
        Lance le processus de peuplement des mails à partir des fichiers dans maildir.
        """
        # Définir des compteurs pour vérifier la cohérence
        total_files = 0
        processed_files = 0
        skipped_files = 0

        folder_to_process = options['folder']
        if folder_to_process:
            folder_path = os.path.join(self.MAIL_DIR, folder_to_process)
            if os.path.isdir(folder_path):
                self.stdout.write(f"Traitement d'un seul dossier: {self.stylize(folder_path, "PURPLE")}")
                stats = self.populateMails(folder_path)
                total_files += stats['total_files']
                processed_files += stats['processed_files']
                skipped_files += stats['skipped_files']
            else:
                self.stdout.write(self.stylize(f"Specified folder '{folder_to_process}' not found.", "ERROR"))
                return
        else:
            for folder in os.listdir(self.MAIL_DIR):
                folder_path = os.path.join(self.MAIL_DIR, folder)
                if os.path.isdir(folder_path):
                    self.stdout.write(f"Traitement du dossier : {self.stylize(folder_path, "PURPLE")}")
                    stats = self.populateMails(folder_path)
                    total_files += stats['total_files']
                    processed_files += stats['processed_files']
                    skipped_files += stats['skipped_files']

        print()
        print(self.stylize("STATISTIQUES DU PEUPLEMENT DES MAILS", "CYAN"))
        print(f"Nombre de fichiers total: {total_files}")
        print(f"Fichiers traités: {processed_files}")
        print(f"Fichiers ignorés (en-tête manquant): {skipped_files}")


    def populateMails(self, folder_path):
        """
        Traite un dossier de mails spécifié pour insérer chaque mail dans la base de données.

        Retourne un dictionnaire contenant des statistiques sur le traitement.
        """
        mail_objects = []
        receiver_objects = []
        email_cache = {}

        # Définir des compteurs pour vérifier la cohérence
        total_files = 0
        processed_files = 0
        skipped_files = 0

        # Parcourir chaque fichier du dossier
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                total_files += 1
                file_path = os.path.join(root, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()

                        # Extraction des en-têtes
                        headers = self.extractMailHeaders(content)
                        if not headers.get('message_id') or not headers.get('date'):
                            skipped_files += 1
                            continue

                        # Récupération de l'id du mail
                        message_id = headers['message_id'][:255]

                        # Extraction et parsing de la date
                        date_mail = self.extractDate(headers['date'])
                        if not date_mail:
                            # Si la date n'est pas parsée correctement, on saute
                            skipped_files += 1
                            continue

                        # Récupération ou création de l'objet Email de l'expéditeur
                        email_address = headers.get('from')
                        x_from = headers.get('x_from')

                        if email_address:
                            email_obj = self.getEmailObj(email_address, x_from, email_cache)
                        else:
                            skipped_files += 1
                            continue

                        first_message_date = self.findFirstMessageDate(content)
                        # Si aucune date pour le premier message, on peut réutiliser date_mail
                        if not first_message_date:
                            first_message_date = date_mail

                        subject = headers.get('subject', '')[:255]
                        main_message = None
                        if subject and "Re:" in subject:
                            main_message = self.extractFirstMessageOnly(content)
                        if main_message is None:
                            main_message = ""

                        # Normalisation du chemin
                        relative_path = os.path.relpath(file_path, self.MAIL_DIR)
                        relative_path = relative_path.replace(os.path.sep, '/')

                        # Création d'une nouvelle instance de Mail
                        new_mail = Mail(
                            id=message_id,
                            filepath=relative_path,
                            subject=subject,
                            date_mail=date_mail,
                            message=self.extractMessageBody(content),
                            is_reply=True if subject and "Re:" in subject else False,
                            main_message=main_message,
                            date_main_message=first_message_date,
                            sender_email_id=email_obj
                        )

                        # Ajout de cette instance dans une liste d'instances qui seront enregistrées plus tard
                        mail_objects.append(new_mail)

                        # Extraction des destinataires et création des Receiver
                        to_addresses = self.extractToAddresses(headers.get('to', ''))
                        new_receivers = self.populateReceivers(to_addresses, new_mail, email_cache)
                        receiver_objects.extend(new_receivers)

                        processed_files += 1

                except Exception as e:
                    self.stdout.write(self.stylize(f"Erreur lors du processus du fichier {file_path}: {str(e)}", "ERROR"))

        try:
            # Enregistrement de tous les mails et destinataires de ce dossier en BDD.
            with transaction.atomic():
                Mail.objects.bulk_create(mail_objects, batch_size=1000)
                self.stdout.write(self.stylize(f"{len(mail_objects)} mails insérés dans la base.", "OK"))
                Receiver.objects.bulk_create(receiver_objects, batch_size=1000)
                self.stdout.write(self.stylize(f"{len(receiver_objects)} destinataires insérés dans la base.", "OK"))
        except IntegrityError as e:
            self.stdout.write(f"{self.stylize("Erreur:", "ERROR")} {e}")

        return {
            'total_files': total_files,
            'processed_files': processed_files,
            'skipped_files': skipped_files
        }


    def populateReceivers(self, to_addresses, mail_obj, email_cache):
        """
        Crée ou récupère un ou plusieurs récepteur(s) associé(s) au mail.
        """
        receiver_objects = []
        for address in to_addresses:
            if not address:
                continue

            email_obj = Email.objects.filter(email_address=address).first()
            if not email_obj:
                external_employee = Employee.objects.create(firstname="Personne", lastname="Externe", category="Externe")
                email_obj = Email.objects.create(email_address=address, employee_id=external_employee)

            if not mail_obj:
                continue

            receiver_objects.append(Receiver(
                email_address_id=email_obj,
                mail_id=mail_obj
            ))
        return receiver_objects


    def extractToAddresses(self, to_field):
        if not to_field:
            return []
        return re.findall(r'[\w\.-]+@[\w\.-]+', to_field)


    def extractMailHeaders(self, content):
        """
        Extrait les en-têtes d'un mail (à partir de son contenu).
        Inclut le champ X-From.
        """
        headers = {}
        headers['message_id'] = self.safeExtract(r'^Message-ID: (.+)', content)
        headers['date'] = self.safeExtract(r'^Date: (.+)', content)
        headers['from'] = self.safeExtract(r'^From: (.+)', content)
        headers['to'] = self.safeExtract(r'^To: (.+)', content)
        headers['subject'] = self.safeExtract(r'^Subject: (.*)', content)
        headers['x_from'] = self.safeExtract(r'^X-From: (.+)', content)  # Nouveau champ
        return headers


    def safeExtract(self, pattern, content):
        """
        Extrait une valeur à partir d'un contenu en utilisant une expression régulière.
        """
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


    def extractMessageBody(self, content: str) -> str:
        """
        Extrait le corps du message principal à partir du contenu du mail.
        """
        match_obj = re.search(r'\n\n(.*)', content, re.DOTALL)
        if match_obj:
            return match_obj.group(1).strip()
        return ""


    def extractFirstMessageOnly(self, content: str) -> str:
        """
        Extrait uniquement le premier message d'un mail.
        """
        parts = content.split("\n\n", 1)
        if len(parts) < 2:
            return ""

        body = parts[1]
        body_cleaned = re.split(r'\nFrom: |\n-{2,} Forwarded by', body, maxsplit=1)[0]
        return body_cleaned.strip()


    def parseXFrom(self, x_from: str):
        """
        Parse le champ X-From pour extraire un nom et une adresse e-mail.
        """
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        name_pattern = r'["<](.*?)[">]|([\w\s]+)'
        
        # Extraire l'adresse email
        email_match = re.search(email_pattern, x_from)
        email = email_match.group(0) if email_match else None

        # Extraire le nom
        name_match = re.search(name_pattern, x_from)
        if name_match:
            name = name_match.group(1) or name_match.group(2)
        else:
            name = "Inconnu"  # Nom par défaut si introuvable

        return name.strip() if name else None, email


    def findFirstMessageDate(self, content: str):
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


    def getEmailObj(self, from_email: str, x_from: str, email_cache: dict) -> Email:
        """
        Récupère ou crée un objet Email pour une adresse e-mail donnée.
        Si l'adresse n'existe pas, crée un employé à partir de X-From.
        """
        if from_email in email_cache:
            return email_cache[from_email]

        email_obj = Email.objects.filter(email_address=from_email).first()
        if not email_obj:
            # Extraire le nom à partir du champ X-From
            name, email = self.parseXFrom(x_from)

            # Si l'email est introuvable dans X-From, utiliser une valeur par défaut
            if not email:
                email = from_email

            # Créer un nouvel employé
            employee = Employee.objects.create(
                firstname=name.split(" ")[0] if name else "Inconnu",
                lastname=" ".join(name.split(" ")[1:]) if name else "Externe",
                category="Externe"
            )

            # Créer l'email
            email_obj = Email.objects.create(
                email_address=email,
                employee_id=employee
            )

        email_cache[from_email] = email_obj
        return email_obj


    def deleteAll(self):
        """
        Supprime toutes les données contenues dans la BDD.
        """
        try:
            Receiver.objects.all().delete()
            Mail.objects.all().delete()
            Email.objects.all().delete()
            Employee.objects.all().delete()
            print(self.stylize("Toutes les données ont été supprimées.", "OK"))
        except Exception as e:
            print(f"{self.stylize("Erreur lors de la suppression :", "ERROR")} {str(e)}")