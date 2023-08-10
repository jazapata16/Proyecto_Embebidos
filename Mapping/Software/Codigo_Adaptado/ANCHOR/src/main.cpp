#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "DW1000Ranging.h"
#include <ArduinoOTA.h>
//este
//ID ANCHOR1
//#define ANCHOR_ADD "85:17:5B:D5:A9:9A:E2:9C"
// ip 192.168.3.9

//ID ANCHOR2
#define ANCHOR_ADD "86:17:5B:D5:A9:9A:E2:9C"
// ip 192.168.3.10

#define UWB_RST 27 
#define UWB_IRQ 34 
#define UWB_SS 4  

const char *ssid = "Xtrim_Zapata";//"Laboratorio_Data";
const char *password = "yoyo.1266";//"D@ta1420";

void newRange(){
    Serial.print("from: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getShortAddress(), HEX);
    Serial.print("\t Range: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getRange());
    Serial.print(" m");
    Serial.print("\t RX power: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getRXPower());
    Serial.println(" dBm");
}

void newBlink(DW1000Device *device){
    Serial.print("blink; 1 device added ! -> ");
    Serial.print(" short:");
    Serial.println(device->getShortAddress(), HEX);
}

void inactiveDevice(DW1000Device *device){
    Serial.print("delete inactive device: ");
    Serial.println(device->getShortAddress(), HEX);
}

void setup(){
    Serial.begin(115200);
    delay(1000);
    DW1000Ranging.initCommunication(UWB_RST, UWB_SS, UWB_IRQ); // Reset, CS, IRQ pin
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachBlinkDevice(newBlink);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);

    DW1000.setChannel(2);
    DW1000.commitConfiguration();
    
    DW1000Ranging.startAsAnchor(ANCHOR_ADD, DW1000.MODE_LONGDATA_RANGE_LOWPOWER, false);

    Serial.print("Connecting to SSID ---> ***** "+String(ssid)+" ***** "+"\n");
    WiFi.mode(WIFI_STA);

    WiFi.begin(ssid, password);

    int wifi_cont = 0;
    while (WiFi.status() != WL_CONNECTED){
        if(wifi_cont > 80){
        Serial.println("");
        Serial.println("Connection Failed! Rebooting...");
        Serial.println("Rebooting...");
        delay(500);
        ESP.restart();
        }
        if(wifi_cont%2 == 0)
        Serial.printf("Connecting... %c%\r", 47);
        else 
        Serial.printf("Connecting... %c%\r", 92);
        wifi_cont++;
        delay(150);
    }
    Serial.println("");
    Serial.println("Wifi Connected!");
    Serial.print("IP Address:");
    Serial.println(WiFi.localIP());
}


void loop(){
    DW1000Ranging.loop();
}