//déclaration des bibliothèques utilisé
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_PN532.h>

// déclaration des capteurs
#define DHT_PIN 13
#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

int sensorValue;

Adafruit_PN532 nfc(4, 5);

// paramètres pour la connection au wifi et au serveur MQTT
const char* ssid = "G10-SAE-hopital";
const char* password = "G10-SAE-hopital";
const char* mqtt_server = "10.2.2.248";

const char* mqtt_user = "esp_Block_OP";
const char* mqtt_mdp = "esp_Block_OP";

WiFiClient esp;
PubSubClient client(esp);

// fonction pour la connexion au wifi
void setup_wifi() {
  delay(10);
  Serial.print("\nConnexion a ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);        
  WiFi.disconnect(true);      
  delay(100);                 

  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connecte !");
  Serial.print("Adresse IP: ");
  Serial.println(WiFi.localIP());
}

// fonction pour la connexion au serveur MQTT
void reconnect() {
  while (!client.connected()) {
    if (client.connect("esp32_coeur", mqtt_user, mqtt_mdp)) {
      Serial.println("Connecté au Broker !");      
    } 
    else {
      Serial.print("Echec, code d'erreur = ");
      Serial.print(client.state());
      Serial.println(" Réessai dans 5 secondes");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  
  dht.begin();
  Wire.begin(); 
  
  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("PN532 non trouvé ! (Vérifiez le câblage et les interrupteurs I2C)");
  } else {
    Serial.println("NFC Elechouse Prêt !");
    nfc.SAMConfig(); 
  }

  Serial.println("Systeme pret !");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  /*-------------------------------------------*/
  // capteur d'humidité
  float humi  = dht.readHumidity();
  float temp = dht.readTemperature();

  if (isnan(humi) || isnan(temp)) {
    Serial.println("Echec de lecture du capteur DHT11");
  } else {
    Serial.print("DHT11# Humidité: ");
    Serial.print(humi);
    Serial.print("%");

    Serial.print("  |  "); 

    Serial.print("Temperature: ");
    Serial.print(temp);
    Serial.println("°C ");
  }

  String tempStr = String(temp);
  String humiStr = String(humi);

  // publication des données du capteur de température sur le serveur MQTT
  client.publish("BlockOP/temp", tempStr.c_str(), true);
  client.publish("BlockOP/humi", humiStr.c_str(), true);

  /*-------------------------------------------*/
  // capteur qualité de l'air
  sensorValue = analogRead(34);
  Serial.print("Qualité de l'air= ");
  Serial.println(sensorValue);

  char gaz[10];
  snprintf(gaz, 10, "%d", sensorValue);
  client.publish("BlockOP/gaz", gaz, true);

  /*-------------------------------------------*/
  // capteur RFID
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
  uint8_t uidLength;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength, 50);

  if (success) {
    Serial.print("NFC trouvé ! UID: ");
    
    String uidString = "";
    for (uint8_t i=0; i < uidLength; i++) {
      if (uid[i] < 0x10) uidString += "0";
      uidString += String(uid[i], HEX);
      Serial.print(uid[i], HEX);
      Serial.print(" ");
    }
    Serial.println("");    
    uidString.toUpperCase();
    client.publish("BlockOP/RFID", uidString.c_str(), true);
  }
  
  delay(2000);
}
