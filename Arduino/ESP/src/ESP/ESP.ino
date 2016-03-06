#include "lib_esp.h"

#define MODE3 3
#define MAX_RESTART 5
#define MAX_CONNECTION_TEMPTATIVE 5
#define NETWORK_NAME "\"ESP\""
#define NETWORK_PSWD "\"0123456789\""

bool isHost = false;
bool isConnected = false;

void setup(void){
    Serial.begin(9600);
    ESP8266.begin(115200);
    Serial.println("SCAN");
    Serial.print(getAPList());
    Serial.println("FIN SCAN");
    set_Network();
}

void loop(void){
  delay(3000);
  if(isHost){
    Serial.println("Host");
    Serial.println("liste des IP connectees :");
    Serial.println(esp_get_Joined_Device_IP());
  }else{
    Serial.println("non-Host");
    Serial.print("Connected : ");
    Serial.println(isConnect());
    if(isConnected){
      Serial.println("IP: ");
      Serial.println(esp_get_local_IP().c_str());
    }
  }
}


void set_Network(void){
    eps_restart();
    if (quit_AP()) {
        Serial.println("QUIT AP OK");
    } else {
        Serial.println("QUIT AP Fail");
    }


    if (eps_AT()) {
        Serial.println("AT OK");
    } else {
        Serial.println("AT Fail");
    }

    if (esp_set_wifi_mode_both()) {
        Serial.println("set mode3 ok");
    } else {
        Serial.println("set mode3 err");
    }

    Serial.print("try to join ");
    Serial.println(NETWORK_NAME);
    if (esp_join_Access_Point(NETWORK_NAME, NETWORK_PSWD)) {
        Serial.print("Join ");
        Serial.print(NETWORK_NAME);
        Serial.println(" Success");
        Serial.println("IP: ");
        Serial.println(esp_get_local_IP().c_str());
        isConnected = true;
    }
    else {
        Serial.print("Join ");
        Serial.print(NETWORK_NAME);
        Serial.println(" Fail");
        quit_AP();
        Serial.print("try to create ");
        Serial.print(NETWORK_NAME);
        Serial.println(" Network");
        if (esp_set_Access_Point_Parameters(NETWORK_NAME, NETWORK_PSWD, 3,4)) {
            Serial.print("Create ");
            Serial.print(NETWORK_NAME);
            Serial.println(" Network Success");
            isHost = true;
        }
        else {
            Serial.print("Create ");
            Serial.print(NETWORK_NAME);
            Serial.println(" Network Fail");
        }
    }
}

String isConnect(){
  if(isConnected){
    return "True";
  }
  return "False";
}

String isTheHost(){
  if(isHost){
    return "True";
  }
  return "False";
}



void set(){
  eps_restart();
  if (quit_AP()) {
      Serial.println("QUIT AP OK");
  } else {
      Serial.println("QUIT AP Fail");
  }
  if (esp_set_wifi_mode_both()) {
      Serial.println("set mode3 ok");
  } else {
      Serial.println("set mode3 err");
  }

}
