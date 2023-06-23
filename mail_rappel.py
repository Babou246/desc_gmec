import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Fonction pour envoyer le mail de rappel
def envoyer_rappel():
    # Récupérer la liste des agents avec des tâches en instance dans l'application
    agents = obtenir_agents_avec_taches_en_instance()

    # Récupérer la date actuelle
    date_actuelle = datetime.date.today()

    # Parcourir la liste des agents
    for agent in agents:
        # Déterminer les destinataires en copie du mail de rappel en fonction du rôle de l'agent
        destinataires_copie = []
        if agent.role == 'Chef de service':
            destinataires_copie.append(agent.chef_departement)
        elif agent.role == 'Agent':
            destinataires_copie.append(agent.chef_service)

        # Envoyer le mail de rappel à l'agent, avec les destinataires en copie
        envoyer_mail_rappel(agent.email, destinataires_copie, date_actuelle)

# Fonction pour envoyer le mail de rappel à un agent
def envoyer_mail_rappel(destinataire, destinataires_copie, date_rappel):
    # Configuration des informations du serveur SMTP
    smtp_server = 'smtp.example.com'
    smtp_port = 587
    smtp_username = 'your_username'
    smtp_password = 'your_password'

    # Création de l'objet MIMEMultipart pour le mail
    msg = MIMEMultipart()
    msg['From'] = 'noreply@example.com'
    msg['To'] = destinataire
    msg['Cc'] = ', '.join(destinataires_copie)
    msg['Subject'] = 'Rappel : Tâches en instance dans l\'application'

    # Corps du message
    message = f'''
    Bonjour {destinataire},

    Ce message est un rappel concernant vos tâches en instance dans l'application.
    Veuillez prendre les mesures nécessaires pour traiter ces tâches.

    Date du rappel : {date_rappel}

    Cordialement,
    Votre équipe'''

    # Ajout du corps du message au mail
    msg.attach(MIMEText(message, 'plain'))

    # Envoi du mail via le serveur SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

# Exemple de fonction pour obtenir la liste
