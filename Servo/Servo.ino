#include <ESP32Servo.h>
#include <WiFi.h>
#include <ArduinoOTA.h>
#include <WiFiUdp.h>

 

Servo servo1;
const int servo_pin = 16;
const char* ssid = "WIFI_NAME";
const char* password = "WIFI_PASSWORD";
unsigned long Millis1 = 0;
unsigned long Millis2 = 1000;
const unsigned long interval = 500;
const int udp_port = 12345;
const unsigned int camera_width = 1920;
const unsigned int camera_length = 1080;
WiFiUDP udp;


void setup() {
  //Sets serial monitor baud rate. 
  Serial.begin(115200);
  //Sets servo to the pin it's plugged into on the ESP 32
  servo1.attach(servo_pin);
  //Sets the wifi mode to access point (ESP makes its own wifi that my laptop connects to)
  WiFi.mode(WIFI_AP);
  //sets the name and password of the wifi
  WiFi.softAP(ssid, password);

  //Sets hostname and password for arduino OTA, which is used to upload code wirelessly to the ESP
  ArduinoOTA.setHostname("HOSTNAME");
  ArduinoOTA.setPassword("PASSWORD");

  //begin arduino OTA
  ArduinoOTA.begin();

  //begin recieving UDP packages at the specified port
  udp.begin(udp_port);
}

void loop() {
  ArduinoOTA.handle();
  //Code inside runs if the time interval has passed
  if (millis() - Millis1 >= interval) {
    //Sets timestamp for most recently recieved package to the current time
    Millis1 = millis();
    //gets the size of the packet that was received
    int packetSize = udp.parsePacket();
    //Checks to make sure that the size of the packet is 8 bytes, ensuring the whole package was successfully delivered
    if (packetSize == 8) {
      //creates a list of 8 8-bit (1 byte) integers. This is because we are recieving 2 32 bit integers, which is 8 bytes
      uint8_t buffer[8];
      //reads data from udp, stores it in the list
      udp.read(buffer, 8);
      //Initialize variables
      int x = 0;
      int y = 0;
      //Stores data in the First 4 bytes are the x-coordinate, last 4 are the y coordinate
      memcpy(&x, buffer, 4);
      memcpy(&y, buffer + 4, 4);
      //If x isn't negative, update the sevo position (negative values are used to denote that a face wasn't detected)
      if (x >= 0) {
        servo1.write(180 * x / camera_width);
      }
      //print out coordinates to serial monitor
      Serial.println("X: " + String(x) + " Y: " + String(y));
    }
  }
}
