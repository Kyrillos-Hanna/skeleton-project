#include <ESP32Servo.h>
#include <WiFi.h>
#include <ArduinoOTA.h>
#include <WiFiUdp.h>

 

Servo servo1;
const int servo_pin = 16;
const char* ssid = "my_wifi";
const char* password = "9876543210";
unsigned long Millis1 = 0;
unsigned long Millis2 = 1000;
const unsigned long interval = 500;
const int udp_port = 12345;
const unsigned int camera_width = 1920;
const unsigned int camera_length = 1080;
WiFiUDP udp;


void setup() {
  Serial.begin(115200);
  servo1.attach(servo_pin);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);

  ArduinoOTA.setHostname("Hostname");
  ArduinoOTA.setPassword("Password");

  ArduinoOTA.begin();

  udp.begin(udp_port);
}

void loop() {
  ArduinoOTA.handle();
  if (millis() - Millis1 >= interval) {
    Millis1 = millis();
    int packetSize = udp.parsePacket();
    if (packetSize == 8) {
      uint8_t buffer[8];
      udp.read(buffer, 8);
      int x = 0;
      int y = 0;
      memcpy(&x, buffer, 4);
      memcpy(&y, buffer + 4, 4);
      if (x >= 0) {
        servo1.write(180 * x / camera_width);
      }
      Serial.println("X: " + String(x) + " Y: " + String(y));
    }
  }
}
