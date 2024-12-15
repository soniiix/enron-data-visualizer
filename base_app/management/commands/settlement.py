from django.core.management.base import BaseCommand
from base_app.models import Employee, Email
from base_project.settings import BASE_DIR
import xml.etree.ElementTree as xml

class Command(BaseCommand):
    help = 'Settlement script'
    DATA_DIR = BASE_DIR.parent / "data"
    EMPLOYEES_FILE = DATA_DIR / "employees.xml"

    def handle(self, *args, **options):
        self.stdout.write("--- Début du script ---")

        # Insertion en BDD des employés du fichier XML
        self.setEmployees()


    def setEmployees(self):
        try:
            # Récupérer le contenu du fichier XML
            root = xml.parse(self.EMPLOYEES_FILE).getroot()

            # Parcourir les éléments du fichier
            for child in root:
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
                new_emp = Employee(firstname=firstname, lastname=lastname, category=category)
                new_emp.save()

                # Gérer la liste des emails de l'employé (+mailbox?)
                for email in emails:
                    new_email = Email(adrmail=email, employee_id=new_emp)
                    new_email.save()
            print("Données enregistrées avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'exécution : {str(e)}")


    def deleteAll(self):
        try:
            Employee.objects.all().delete()
            Email.objects.all().delete()
            print("Toutes les données ont été supprimées.")
        except Exception as e:
            print(f"Erreur lors de l'exécution : {str(e)}")

                
        































    """
    try:
            e1 = Employee(id=1, firstname="John", lastname="Doe", category="employé")
            self.stdout.write(f"Employé créé : {e1.firstname} {e1.lastname} ({e1.category})")
            e1.save()
        except Exception as e:
            self.stderr.write(f"Erreur lors de l'utilisation du modèle Employee : {str(e)}")
    """
        
