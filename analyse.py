import argparse
from modules.log_reader import LogReader
from modules.log_analyzer import LogAnalyzer
from modules.log_ai import LogAI  # Importer la classe LogAI pour l'option GPT
from modules.notification import Notification  # Import de la classe Notification
import schedule
import time  # Nécessaire pour le délai entre les exécutions
from datetime import datetime # pour afficher l'heure entre les exécutions

def analyser_logs(args):
    """
    Fonction principale d'analyse des logs. Cette fonction sera appelée à chaque exécution programmée.
    Elle prend les arguments fournis en ligne de commande via l'objet args.
    """
    print(f"\nDémarrage de l'analyse des logs à {datetime.now()}")

    # Créer une instance de LogReader avec le chemin du répertoire
    lecteur = LogReader(args.repertoire)

    # Trouver tous les fichiers de logs correspondant au pattern dans le répertoire
    fichiers_logs = lecteur.trouver_fichiers_logs(pattern=args.pattern)

    # Si des fichiers de logs sont trouvés, les lire un par un et extraire les informations
    if fichiers_logs:
        for fichier_log in fichiers_logs:
            print(f"\nLecture du fichier : {fichier_log}")

        # Option 1 : Utiliser GPT pour analyser les logs avec OpenAI (si --use-gpt est spécifié)
        if args.use_gpt:
            print("\nAnalyse des logs avec GPT via l'API OpenAI...")

            # Lire les logs bruts pour l'analyse avec GPT
            lecteur.lire_logs_bruts(fichier_log)
            # Créer une instance de LogAI avec la liste de logs
            analyseur_ai = LogAI(lecteur.lignes_extraites_brut[:10])  # Limiter à 10 lignes pour l'exemple

            # Analyser les logs avec OpenAI GPT
            try:
                analyseur_ai.analyser_logs_avec_gpt()
                print("Résultat de l'analyse par GPT en JSON :")
                print(analyseur_ai.dump_reponse())  # Afficher la réponse JSON
            except ValueError as e:
                print(e)

        # Option 2 : Analyse traditionnelle des logs (si --use-gpt n'est pas spécifié)
        else:
            lecteur.lire_et_extraire_logs(fichier_log)  # Lire et extraire les informations du fichier de logs
            print("\nAnalyse des logs avec les méthodes traditionnelles...")

            # Créer le DataFrame une fois que tous les fichiers ont été lus
            lecteur.creer_dataframe()

            # Créer une instance de LogAnalyzer pour analyser les logs
            analyseur = LogAnalyzer(lecteur.df_logs)

            # Analyser la fréquence des adresses IP dans l'intervalle de temps spécifié
            lignes_suspectes = analyseur.analyser_frequence_ips(intervalle_temps=args.intervalle, seuil_alerte=args.seuil)

            if lignes_suspectes:
                if args.graphe:
                    # Afficher un graphe des événements critiques
                    analyseur.afficher_evenements_par_date()

                if args.notifier:
                    # Envoyer une notification par email si des événements critiques sont détectés
                    print("Événements critiques détectés, envoi d'une notification par email...")

                    # Créer une instance de Notification avec le fichier de configuration
                    notification = Notification()

                    # Envoyer la notification avec les événements critiques
                    notification.envoyer_notification_evenements_critiques(lignes_suspectes[:10])

                if args.persister:
                    # Persister les événements critiques dans une base de données SQLite
                    print("Persistance des événements critiques dans une base de données SQLite...")
                    analyseur.persister_evenements_critique()
            else:
                print("Aucun événement critique détecté.")

            # Afficher le DataFrame contenant les informations extraites
            # lecteur.afficher_dataframe()
    else:
        print(f"Aucun fichier de logs correspondant au pattern '{args.pattern}' n'a été trouvé dans le répertoire.")

def main():
    # Gestion des arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Script d'analyse de logs")
    parser.add_argument("repertoire", help="Chemin vers le répertoire contenant les fichiers de logs", type=str)
    parser.add_argument("--pattern", help="Pattern pour filtrer les fichiers de logs (par défaut 'secure*')", type=str, default="secure*")
    parser.add_argument("--seuil", help="Seuil d'alerte pour les adresses IP suspectes", type=int, default=10)
    parser.add_argument("--intervalle", help="Intervalle de temps pour l'analyse des accès (par défaut '1min')", type=str, default="1min")
    parser.add_argument("--use-gpt", help="Utiliser GPT pour l'analyse des logs avec OpenAI", action="store_true")
    parser.add_argument("--notifier", help="Notifier les évènements critiques par e-mail", action="store_true")
    parser.add_argument("--graphe", help="Afficher un graphe des évènements critiques", action="store_true")
    parser.add_argument("--persister", help="Persister les évènements critiques dans SQLite", action="store_true")
    parser.add_argument("--planifier",
        help="Planification du script, indiquer le nombre de minutes entre chaque exécution", type=int)
    args = parser.parse_args()

    # Si l'option --planifier est utilisée, planifier l'exécution du script
    if args.planifier:
        print(f"Planification du script toutes les {args.planifier} minutes.")

        # Planifier l'analyse des logs en fonction de l'intervalle spécifié
        schedule.every(args.planifier).minutes.do(analyser_logs, args=args)

        # Boucle infinie pour exécuter les tâches planifiées
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # Si la planification n'est pas spécifiée, exécuter une seule fois
        analyser_logs(args)


if __name__ == "__main__":
    main()