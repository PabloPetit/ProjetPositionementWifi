#include "lib_esp.h"

bool eps_restart(void){
    unsigned long start;
    rx_empty();
    ESP8266.println("AT+RST");
    bool result = recvFind("OK");
    if (result) {
        delay(2000);
        start = millis();
        while (millis() - start < 3000) {
            if (eps_AT()) {
                delay(1500); /* Waiting for stable */
                return true;
            }
            delay(100);
        }
    }
    return false;
}

bool eps_AT(void){
    rx_empty();
    ESP8266.println("AT");
    return recvFind("OK");
}

void rx_empty(void){
    while(ESP8266.available() > 0) {
        ESP8266.read();
    }
}

bool recvFind(String target){
    String data_tmp;
    data_tmp = recvString(target);
    if (data_tmp.indexOf(target) != -1) {
        return true;
    }
    return false;
}

String recvString(String target){
    String data;
    char a;
    unsigned long start = millis();
    while (millis() - start < TIMEOUT) {
        while(ESP8266.available() > 0) {
            a = ESP8266.read();
      if(a == '\0') continue;
            data += a;
        }
        if (data.indexOf(target) != -1) {
            break;
        }
    }
    return data;
}

String recvString2(String target, String target2){
    String data;
    char a;
    unsigned long start = millis();
    while (millis() - start < TIMEOUT) {
        while(ESP8266.available() > 0) {
            a = ESP8266.read();
      if(a == '\0') continue;
            data += a;
        }
        if (data.indexOf(target) != -1 || data.indexOf(target2) != -1) {
            break;
        }
    }
    return data;
}

bool esp_set_wifi_mode_both(void){
    uint8_t mode;
    if (!esp_ask_wifi_mode(&mode)) {
        return false;
    }
    if (mode == 3) {
        return true;
    } else {
        if (esp_set_wifi_mode(3) && eps_restart()) {
            return true;
        } else {
            return false;
        }
    }
}

bool esp_ask_wifi_mode(uint8_t *mode){
    String str_mode;
    bool ret;
    if (!mode) {
        return false;
    }
    rx_empty();
    ESP8266.println("AT+CWMODE?");
    ret = recvFindAndFilter("OK", "+CWMODE:", "\r\n\r\nOK", str_mode);
    if (ret) {
        *mode = (uint8_t)str_mode.toInt();
        return true;
    } else {
        return false;
    }
}

bool recvFindAndFilter(String target, String begin, String end, String &data){
    String data_tmp;
    data_tmp = recvString(target);
    if (data_tmp.indexOf(target) != -1) {
        int32_t index1 = data_tmp.indexOf(begin);
        int32_t index2 = data_tmp.indexOf(end);
        if (index1 != -1 && index2 != -1) {
            index1 += begin.length();
            data = data_tmp.substring(index1, index2);
            return true;
        }
    }
    data = "";
    return false;
}

bool esp_set_wifi_mode(uint8_t mode){
    String data;
    rx_empty();
    ESP8266.print("AT+CWMODE=");
    ESP8266.println(mode);

    data = recvString2("OK", "no change");
    if (data.indexOf("OK") != -1 || data.indexOf("no change") != -1) {
        return true;
    }
    return false;
}

bool esp_join_Access_Point(String ssid, String pwd){
    String data;
    rx_empty();
    ESP8266.print("AT+CWJAP=\"");
    ESP8266.print(ssid);
    ESP8266.print("\",\"");
    ESP8266.print(pwd);
    ESP8266.println("\"");
    data = recvString2("OK", "FAIL");
    if (data.indexOf("OK") != -1) {
        return true;
    }
    else if(data.indexOf("FAIL") != -1){
      return false;
    }
    return false;
}

String esp_get_local_IP(){
    String list;
    rx_empty();
    ESP8266.println("AT+CIFSR");
    recvFindAndFilter("OK", "\r\r\n", "\r\n\r\nOK", list);
    return list;
}

String esp_get_Joined_Device_IP(void){
    String list;
    rx_empty();
    ESP8266.println("AT+CWLIF");
    recvFindAndFilter("OK", "\r\r\n", "\r\n\r\nOK", list);
    return list;
}

bool esp_set_Access_Point_Parameters(String ssid, String pwd, uint8_t chl, uint8_t ecn){
    String data;
    rx_empty();
    ESP8266.print("AT+CWSAP=\"");
    ESP8266.print(ssid);
    ESP8266.print("\",\"");
    ESP8266.print(pwd);
    ESP8266.print("\",");
    ESP8266.print(chl);
    ESP8266.print(",");
    ESP8266.println(ecn);

    //TODO : ré-ecrire data et data2 pour ne pas attentre 20sec
    data = recvString2("OK", "ERROR");
    if (data.indexOf("OK") != -1) {
        return true;
    }
    return false;
}

bool quit_AP(void){
    String data;
    rx_empty();
    ESP8266.println("AT+CWQAP");
    return recvFind("OK");
}
