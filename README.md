# SAÉ 502 Piloter un projet informatique
 
 
La SAE 502 a eu pour objectif de nous faire construire le réseau informatique d'une clinique de campagne. 
Nous avons donc été amenés à créer le réseau en mettant par exemple en place des switchs, des VLAN, un VPN, un hyperviseur (Proxmox) et un firewall. 
Nous avons aussi créé et mis en place un réseau IOT pour permettre la récupération de plusieurs données en utilisant plusieurs types de capteurs comme des capteurs de température, d'humidité ou RFID pour répondre aux besoins de l'hôpital (ex : dans une chambre froide il y a besoin de sécuriser l'accès avec un capteur RFID et de connaître la température de la pièce). 
Pour finir, nous avons également fait une application métier pour permettre aux médecins, patients et agents de sécurité d'accéder aux informations qu'ils pourraient avoir besoin (flux vidéo des caméras pour les agents de sécurité, l'emplacement des médicaments destinés à un patient pour les médecins et les informations sur le traitement que le patient va devoir subir).
 
 
Pour répondre aux besoins de la clinique de campagne, nous avons fait un schéma du système. Ci-dessous vous trouverez une version simplifiée de ce dernier, pour la version plus complète, cette dernière se trouve dans le sommaire des fichiers et dossiers ci-dessus et correspond au fichier "Diagramme du réseau.drawio" (fichier à ouvrir dans l'application Draw.io).
<img width="1142" height="702" alt="Capture d&#39;écran 2026-10-27 175008" src="https://github.com/user-attachments/assets/08139f3a-3e88-4c94-ac5f-fbbe39fe48e0" />


## Partie Réseau
Dans la partie réseau, à la suite de la découverte des besoins de la clinique, nous avons décidé de mettre le réseau de la façon ci-dessous.
<img width="1812" height="815" alt="SchemaReseauSAE502" src="https://github.com/user-attachments/assets/d47c79f2-8a34-4d35-986a-d1b87572a0bc" />

Nous avons choisi de faire le réseau de cette manière car nous avons voulu protéger au maximum le réseau, d'où la présence d'un firewall, de VLAN, d'un réseau wifi invité, d'un réseau wifi pour les capteurs IOT, etc.  

 
## Partie IOT
Pour la partie IOT, nous avons décidé d'organiser ce réseau comme l'image ci-dessus où l'on a, dans un premier temps, les capteurs qui relèvent les données. Ces derniers envoient ensuite ces données aux microcontrôleurs auxquels ils sont connectés pour qu'ils se chargent d'envoyer les données (mosquitto_pub) sur les topics définis sur le serveur (BlockOP/temp pour la température du bloc opératoire).
<img width="1127" height="497" alt="Capture d&#39;écran 2026-10-27 182307" src="https://github.com/user-attachments/assets/18921686-074e-4c07-b38a-18a6bba93b10" />

Après que le serveur MQTT reçoit les données, il se charge d'envoyer ces données sur NodeRed qui est une application no code (sans code à créer) permettant d'effectuer des actions sur des flux de données. Pour faire ces actions, il s'abonne sur des topics grâce au bloc MQTT IN (bloc violet avec le nom BlockOP/temp) et grâce à des blocs comme "requête http", il est possible de faire des requêtes HTTP vers par exemple l'application métier. 
<img width="1226" height="664" alt="NodeRedSchéma" src="https://github.com/user-attachments/assets/e97b481d-414e-413d-b6ab-366dc07176f1" />
