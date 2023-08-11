#include <SPI.h>
//necesarias para oled
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
//
#include <HampelFilter.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>
#include "DW1000Ranging.h"
#include "link.h"

//DEFINO TAMANIO DE OLED
#define I2C_SDA 21
#define I2C_SCL 22

#define SCREEN_WIDTH 128 // OLED display width,  in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
// declare an SSD1306 display object connected to I2C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

//este
#define DW_PIN_RST 27 
#define DW_PIN_IRQ 34
#define DW_PIN_SS 4
//192.168.3.11
#define ADD_TAG "7D:22:22:EA:82:60:3B:9C"
#define SERIAL_DEBUG false

const char *ssid = "Xtrim_Zapata";//"Laboratorio_Data";
const char *password = "yoyo.1266";//"D@ta1420";

//UDP
String WIFI_IP = "192.168.3.11";//"192.168.8.75";
String WIFI_MASK= "255.255.255.0";

String WIFI_GATEWAY="192.168.3.1";// "192.168.8.254";
String WIFI_DNS="192.168.3.1";// "132.142.160.6";

const char *UDP_IP_server = "192.168.3.224";//"172.27.206.153";
const int16_t UDP_port = 8080;




struct MyLink *uwb_data;
int index_num = 0;
long runtime = 0;
long runtime_display = 0;
String all_json = "";

int ANCHORS[] = {0x8517,0x1785,0x1786,0x8617};
const float offsetsA[] = {0.78,0.60,0.52,0.85};
float range_row_A[] = {0.0,0.0,0.0,0.0};
float range_filtered_A[] = {0.0,0.0,0.0,0.0};
int buffer_init_A[] = {0,0,0,0};
HampelFilter dataBufferA[] = {HampelFilter(0.00, 10, 40.0),HampelFilter(0.00, 10, 40.0),HampelFilter(0.00, 10, 40.0),HampelFilter(0.00, 10, 40.0)};

TaskHandle_t Task1;
WiFiUDP udp;

int getIpBlock(int index, String str){
  char separator = '.';
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = str.length()-1;
  
  for(int i=0; i<=maxIndex && found<=index; i++){
    if(str.charAt(i)==separator || i==maxIndex){
      found++;
      strIndex[0] = strIndex[1]+1;
      strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }
  return found>index ? str.substring(strIndex[0], strIndex[1]).toInt() : 0;
}

IPAddress str2IP(String str){
  IPAddress ret( getIpBlock(0,str),getIpBlock(1,str),getIpBlock(2,str),getIpBlock(3,str));
  return ret;
}

int find (int address, int *ANCHORS){
  int longitud = sizeof(ANCHORS);
  int i;
  for (i=0; i<longitud;i++ ){
    if (address==ANCHORS[i]){
      return 1;
    }
  }
  return 0; 
}

int indice (int address, int *ANCHORS){
  int longitud = sizeof(ANCHORS);
  int i;
  for (i=0; i<longitud;i++ ){
    if (address==ANCHORS[i]){
      return i;
    }
  }
  return 0; 
}


void newRange() {

  if(find(DW1000Ranging.getDistantDevice()->getShortAddress(),ANCHORS) && DW1000Ranging.getDistantDevice()->getRange() > 0){
    int indic= indice(DW1000Ranging.getDistantDevice()->getShortAddress(),ANCHORS);
    range_row_A[indic] = DW1000Ranging.getDistantDevice()->getRange()*offsetsA[indic];
    if(buffer_init_A[indic] <= 20){
      dataBufferA[indic].write(range_row_A[indic]);
      buffer_init_A[indic]++;
    }else{
      if(!dataBufferA[indic].checkIfOutlier(range_row_A[indic])){
        range_filtered_A[indic] = range_row_A[indic];
      }
      dataBufferA[indic].write(range_row_A[indic]);
    }
    fresh_link(uwb_data, DW1000Ranging.getDistantDevice()->getShortAddress(), range_filtered_A[indic], DW1000Ranging.getDistantDevice()->getRXPower());
  }
}

void newDevice(DW1000Device* device) {
  add_link(uwb_data, device->getShortAddress());
}

void inactiveDevice(DW1000Device* device) {
  delete_link(uwb_data, device->getShortAddress());
}

void display_uwb(struct MyLink *p){
    struct MyLink *temp = p;
    int row = 0;
    display.clearDisplay(); // clear display

    display.setTextSize(1);         // set text size
    display.setTextColor(SSD1306_WHITE);    // set text color
    display.setCursor(0, 10);       // set position to display
    display.println("HOLA"); // set text
    display.display();              // display on OLED

    if (temp->next == NULL){

        return;
    }
    while (temp->next != NULL){
        temp = temp->next;
        char c[30];
        //sprintf(c, "%x %.1fm", temp->anchor_addr, temp->range[0]);

        if (row >= 4){
          break;
        }
    }

    return;
}

void send_udp(String *msg_json){

  udp.beginPacket(UDP_IP_server, UDP_port);
  udp.print(*msg_json);
  udp.endPacket();
}

void Task1code( void * pvParameters ){
  Wire.begin(I2C_SDA,I2C_SCL);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();


  while (true){
    if ((millis() - runtime) > 300){
        make_link_json(uwb_data, &all_json);
        send_udp(&all_json);
        runtime = millis();
    }
    if ((millis() - runtime_display) > 1000){
        display_uwb(uwb_data);
        runtime_display = millis();
    }
    delay(10);
  }
}

void setup() {
  Serial.begin(115200);

  DW1000Ranging.initCommunication(DW_PIN_RST, DW_PIN_SS, DW_PIN_IRQ); //Reset, CS, IRQ pin
  //define the sketch as anchor. It will be great to dynamically change the type of module
  DW1000Ranging.attachNewRange(newRange);
  DW1000Ranging.attachNewDevice(newDevice);
  DW1000Ranging.attachInactiveDevice(inactiveDevice);

  DW1000.enableDebounceClock();
  DW1000.enableLedBlinking();
  DW1000.setGPIOMode(MSGP0, LED_MODE);
  DW1000.commitConfiguration();

  //we start the module as a tag
  DW1000Ranging.startAsTag(ADD_TAG, DW1000.MODE_LONGDATA_RANGE_LOWPOWER, false);

  uwb_data = init_link();
  delay(100);

  Serial.print("Connecting to SSID ---> ***** "+String(ssid)+" ***** "+"\n");
  WiFi.mode(WIFI_STA);
  WiFi.config(str2IP(WIFI_IP),str2IP(WIFI_GATEWAY),str2IP(WIFI_DNS));
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
  xTaskCreatePinnedToCore(
              Task1code,   /* Task function. */
              "Task1",     /* name of task. */
              10000,       /* Stack size of task */
              NULL,        /* parameter of the task */
              1,           /* priority of the task */
              &Task1,      /* Task handle to keep track of created task */
              0);          /* pin task to core 0 */
  delay(500);

  // initialize OLED display with I2C address 0x3C
  // 
  // if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
  //   Serial.println(F("failed to start SSD1306 OLED"));
  //   while (1);
  // }
         // wait two seconds for initializing
  // display.clearDisplay(); // clear display

  // display.setTextSize(1);         // set text size
  // display.setTextColor(WHITE);    // set text color
  // display.setCursor(0, 10);       // set position to display
  // display.println("HOLA"); // set text
  // display.display();              // display on OLED

}

void loop() {
  DW1000Ranging.loop();
}