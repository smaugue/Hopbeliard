#déclaration du langage bash
#!/bin/bash 

#permet de récupérer les informations d'une carte RFID, récupérer la ligne UID puis récupérer uniquement le numéro qui l'identifie (en enlevant UID)
infoCarte=$(nfc-list | grep "UID" | awk -F': ' '{print $2}')

#publie l'information vers le serveur MQTT
mosquitto_pub -h 10.2.2.248 -p 1883 -t "test/RFID" -m "$infoCarte";
