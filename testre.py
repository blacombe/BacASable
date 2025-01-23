import re

# Exemple de ligne de log
log_line = "Sep 29 03:29:38 localhost sshd[3396462]: Invalid user roott from 89.208.103.230 port 57294"

# Expression rationnelle
regex = r"([A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2}) .* (Invalid user|Failed password) (\w+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

# Extraction des informations
match = re.search(regex, log_line)
if match:
    date_heure = match.group(1)
    evenement = match.group(2)
    utilisateur = match.group(3)
    adresse_ip = match.group(4)

    print(f"Date et heure : {date_heure}")
    print(f"Événement : {evenement}")
    print(f"Utilisateur : {utilisateur}")
    print(f"Adresse IP : {adresse_ip}")