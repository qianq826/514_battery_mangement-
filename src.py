#include <Arduino.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

// Firebase credentials
#define FIREBASE_HOST "https://zia-esp32-wificonnection-default-rtdb.firebaseio.com/"
#define FIREBASE_AUTH "AIzaSyDoPnD0orM6TqoL5nGlEfmJzfpgqEeg9Z8"
#define WIFI_SSID "UW MPSK"
#define WIFI_PASSWORD "YuA^y-x#5k"

// Ultrasonic Sensor Pins
const int trigPin = D2; // Change according to your setup
const int echoPin = D3; // Change according to your setup

// Firebase objects
FirebaseData firebaseData;
FirebaseAuth auth;
FirebaseConfig config;

// Function prototypes
float measureDistance();
void connectToWiFi();
void initFirebase();
void sendDataToFirebase(float distance);

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  connectToWiFi();
  initFirebase();
}

void loop() {
  float distance = measureDistance();
  sendDataToFirebase(distance);

  // Put the device to sleep to save power if the distance is more than 50 cm
  if (distance > 50.0) {
    Serial.println("No significant movement detected, going to sleep.");
    esp_sleep_enable_timer_wakeup(30 * 1000000); // Wake up after 30 seconds
    esp_deep_sleep_start();
  }
  
  delay(1000); // Adjust based on your needs
}

float measureDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  float distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)
  Serial.print("Distance: ");
  Serial.println(distance);
  return distance;
}

void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());
}

void initFirebase() {
  config.api_key = FIREBASE_AUTH;
  config.database_url = FIREBASE_HOST;
  
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

void sendDataToFirebase(float distance) {
  if (Firebase.ready()) {
    if (Firebase.RTDB.setFloat(&firebaseData, "/sensor/distance", distance)) {
      Serial.println("Distance data sent to Firebase");
    } else {
      Serial.print("Error sending to Firebase: ");
      Serial.println(firebaseData.errorReason());
    }
  }
}

