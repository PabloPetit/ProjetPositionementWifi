#include "ESP8266.h"

#define SSID        "ESP2"
#define PASSWORD    "password"

bool isHost = false;
ESP8266 esp;
void setup(void){
    Serial.begin(9600);
    Serial1.begin(115200);
    esp = ESP8266();


}

void loop(void){
  delay(100);
  Serial.println(esp.getAPList());
}
