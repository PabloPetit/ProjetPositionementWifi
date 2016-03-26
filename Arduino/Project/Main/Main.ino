#include "ESP8266.h"

#define SSID        "HONOR_KIW-L21_E44A"
#define PASSWORD    "catalina"
#define PORT        3553

bool isHost = false;
ESP8266 esp;
void setup(void){
    Serial.begin(9600);
    Serial1.begin(115200);
    esp = ESP8266();
    bool res = esp.joinAP(SSID, PASSWORD);
    Serial.println(res);


}

void loop(void){
  delay(100);
  //Serial.println(esp.getAPList());
}

bool connect_to_Server();
