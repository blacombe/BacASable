import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sqlite3

class LogAnalyzer:
    def __init__(self, df_logs):
        """
        Constructeur qui initialise l'objet LogAnalyzer avec un DataFrame contenant les logs extraits.

        Paramètres :
        df_logs (pd.DataFrame) : Le DataFrame contenant les informations extraites des logs.
        """
        self.df_logs = df_logs
        # Convertir la colonne 'DateHeure' en datetime si ce n'est pas déjà fait
        self.__convertir_colonne_datetime('DateHeure')

    def __convertir_colonne_datetime(self, colonne):
        """
        Convertit la colonne spécifiée en type datetime si elle n'est pas déjà typée.
        :param colonne: Le nom de la colonne à vérifier et convertir
        """
        # Vérifier si la colonne n'est pas déjà de type datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df_logs[colonne]):
            print(f"Conversion de la colonne '{colonne}' en datetime.")

            # Ajouter l'année courante aux dates avant de les convertir en datetime
            self.df_logs[colonne] = self.df_logs[colonne].apply(lambda x: f"{x} {datetime.now().year}")
            try:
                self.df_logs[colonne] = pd.to_datetime(self.df_logs[colonne], format='%b %d %H:%M:%S %Y')
            except Exception as e:
                print(f"Erreur lors de la conversion des dates : {e}")
                return
        else:
            print(f"La colonne '{colonne}' est déjà typée en datetime.")

    def analyser_frequence_ips(self, intervalle_temps='1min', seuil_alerte=10):
        """
        Analyse la fréquence d'accès des adresses IP dans un intervalle de temps.
        Détecte les adresses IP suspectes qui accèdent trop souvent dans un court laps de temps.

        Paramètres :
        intervalle_temps (str) : Intervalle de temps pour l'analyse (par exemple, '1min' pour une minute).
        seuil_alerte (int) : Nombre d'accès au-delà duquel une adresse IP est considérée comme suspecte.
        """
        if not self.df_logs.empty:

            # Grouper par adresse IP et intervalle de temps
            acces_par_ip = self.df_logs.set_index('DateHeure').groupby(
                [pd.Grouper(freq=intervalle_temps), 'AdresseIP']
            ).size()

            # Filtrer les groupes qui dépassent le seuil d'alerte
            acces_suspects = acces_par_ip[acces_par_ip > seuil_alerte]

            # Afficher les résultats
            if not acces_suspects.empty:
                print(f"\nAccès suspects détectés (plus de {seuil_alerte} accès par IP dans {intervalle_temps}) :")
                # return acces_suspects.tolist()
                return [(index_tuple, valeur) for index_tuple, valeur 
                        in zip(acces_suspects.index, acces_suspects.values)]
            else:
                print(f"Aucun accès suspect détecté dans l'intervalle de {intervalle_temps}.")
        else:
            print("Le DataFrame est vide. Veuillez charger les logs avant l'analyse.")

    def afficher_evenements_par_date(self):
        """
        Affiche un graphique de l'évolution des événements critiques par date.
        :param logs_df: DataFrame Pandas contenant les logs avec une colonne 'Date/Heure'.
        """
        if not self.df_logs.empty:
            # Compter le nombre d'événements critiques par jour
            evenements_par_date = self.df_logs.groupby(self.df_logs['DateHeure'].dt.date).size()

            # Créer le graphique linéaire
            plt.figure(figsize=(10, 6))
            plt.plot(evenements_par_date.index, evenements_par_date.values, marker='o', linestyle='-', color='blue')

            # Ajouter des titres et des labels
            plt.title("Évolution des événements critiques par date")
            plt.xlabel("Date")
            plt.ylabel("Nombre d'événements critiques")

            # Afficher le graphique
            plt.grid(True)
            plt.xticks(rotation=45)  # Rotation des dates pour une meilleure lisibilité
            plt.tight_layout()
            plt.show()

    def persister_evenements_critique(self):
        cn = sqlite3.connect('logs_analyses.db')

        # Créer un curseur pour exécuter des requêtes SQL
        cur = cn.cursor()

        # Créer une table pour stocker les événements critiques, si elle n'existe pas déjà
        cur.execute('''
            CREATE TABLE IF NOT EXISTS evenement_suspect (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_heure DATETIME,
                evenement TEXT,
                utilisateur TEXT,
                adresse_ip TEXT
            )
        ''')

        # Sauvegarder les changements
        cn.commit()

        # Parcourir les logs et insérer chaque ligne dans la base de données
        for index, ligne in self.df_logs.iterrows():
            cur.execute('''
                INSERT INTO evenement_suspect (date_heure, evenement, utilisateur, adresse_ip)
                VALUES (?, ?, ?, ?)
            ''', (ligne['DateHeure'].strftime('%Y-%m-%d %H:%M:%S'), ligne['Evenement'], 
                  ligne['Utilisateur'], ligne['AdresseIP']))

        # Sauvegarder les changements
        cn.commit()
        cn.close()