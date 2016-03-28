#include "ESP8266.h"
#include "Message.h"

//#define SSID        "HONOR_KIW-L21_E44A"
#define SSID        "adequin_renaud_95110"

//#define PASSWORD    "catalina"
#define PASSWORD    "1234567890"
#define SERVER_ADDR "192.168.0.10"
#define PORT        4015

int self_ID;

bool isHost = false;
ESP8266 esp;
void setup(void){
    Serial.begin(9600);
    Serial1.begin(115200);
    esp = ESP8266();
    // connect to AP
    bool res = esp.joinAP(SSID, PASSWORD);
    Serial.println(res);

    // Create TCP
    res = esp.createTCP(SERVER_ADDR, PORT);
    Serial.println(res);
    int h = getId(esp);
    Serial.println(h);


    /**
    * SETUP:
    * X Connect to AP
    * - Connect to server (TCP)
    * - Recuperer la liste des ancres
    *
    * LOOP:
    * - get range evalualtion
    * -
    */


}

void loop(void){
  delay(100);
  //Serial.println(esp.getAPList());
}


bool connect_to_Server(){

}
