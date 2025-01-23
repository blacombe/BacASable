import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

class Notification:
    def __init__(self):
        # Lire la configuration depuis le fichier config.ini
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # Charger les paramètres SMTP depuis la section [smtp]
        self.smtp_server = self.config['smtp']['server']
        self.smtp_port = int(self.config['smtp']['port'])
        self.smtp_user = self.config['smtp']['user']
        self.smtp_password = self.config['smtp']['password']

        # Charger le destinataire depuis la section [email]
        self.recipient = self.config['email']['recipient']

    def envoyer_email(self, sujet, contenu):
        """
        Envoie un email avec le sujet et le contenu spécifiés.
        """
        # Créer le message email
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = self.recipient
        msg['Subject'] = sujet

        # Ajouter le corps de l'email
        msg.attach(MIMEText(contenu, 'plain'))

        try:
            # Connexion au serveur SMTP
            serveur = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
            serveur.ehlo()  # Pour s'identifier auprès du serveur (nécessaire pour certains serveurs)

             # Démarrer la connexion TLS
            serveur.starttls()  # Passage à une connexion sécurisée TLS
            # serveur.ehlo()  # S'identifier à nouveau après le passage en TLS

            serveur.login(self.smtp_user, self.smtp_password)  # Authentification

            # Envoyer l'email
            serveur.sendmail(self.smtp_user, self.recipient, msg.as_string())

            print(f"Email envoyé avec succès à {self.recipient}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
        finally:
            if serveur:
                serveur.quit()

    def envoyer_notification_evenements_critiques(self, logs_critiques):
        """
        Prépare et envoie un email contenant les événements critiques détectés dans les logs.
        """
        sujet = "Alerte : Événements critiques détectés dans les logs"
        contenu = "Bonjour,\n\nLes événements suivants ont été détectés comme critiques dans les logs :\n\n"

        # Ajouter chaque événement critique au contenu de l'email
        for log in logs_critiques:
            contenu += f"- {log}\n"

        contenu += "\nVotre système de surveillance."

        # Envoyer l'email
        self.envoyer_email(sujet, contenu)