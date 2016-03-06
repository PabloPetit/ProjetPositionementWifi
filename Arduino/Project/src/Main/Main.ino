#include "lib_esp.h"
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiServer.h>
#include <WiFiUdp.h>
struct scan_config {
  String ssid;       // AP’s ssid
  int rssi;      // AP’s bssid
  int channel;     //scan a specific channel
  int enc;
  String mac;
};

void setup() {
  Serial.begin(9600);
  //ESP8266.begin(115200);
  delay(1000);
  Serial.println("-----");
  //String status = getIPStatus();
  //Serial.print(status);
  Serial.println("-----");
  Serial.print(WiFi.status());
  Serial.println("-----");

  /*String liste = getAPList();
  struct scan_config l[10];
  split(l, liste, '\n');
  Serial.println(l[0].ssid);*/

}

void loop() {

}

void split(struct scan_config l[], String line, char sep){
  int i = 0;
  int startIndex = 0;
  int endIndex = 0;

  ;
  while ((endIndex = line.indexOf(sep, startIndex)) != -1 && i < 9) {
    l[i] = scan_config();
    String s = line.substring(startIndex, endIndex);
    set_ap(s, &l[i]);
    startIndex = endIndex+1;
    i++;

  }
  String s = line.substring(startIndex, line.length());
  set_ap(s, &l[i]);
}

void set_ap(String line, scan_config *tmp){
  // ENC
  int index = line.indexOf('(')+1;
  String  myString = line.substring(index, index+1);;
  int myStringLength = myString.length()+1;
  char myChar[myStringLength];
  myString.toCharArray(myChar,myStringLength);
  tmp->enc = atoi(myChar);

  //SSID
  int start = index+2;
  int end = line.indexOf(',', start);
  tmp->ssid = line.substring(start, end);

  // RSSI
  start = end+1;
  end = line.indexOf(',', start);
  myString = line.substring(start, end);
  myStringLength = myString.length()+1;
  char myChar2[myStringLength];
  myString.toCharArray(myChar2,myStringLength);
  tmp->rssi = atoi(myChar2);

  //MAC
  start = end+1;
  end = line.indexOf(',', start);
  tmp->mac = line.substring(start, end);

  //CHANNEL
  start = end+1;
  end = line.indexOf(',', start);
  myString = line.substring(start, end);
  myStringLength = myString.length()+1;
  char myChar23[myStringLength];
  myString.toCharArray(myChar23,myStringLength);
  tmp->channel = atoi(myChar23);
}


/***
int commaIndex = myString.indexOf(',');
int secondCommaIndex = myString.indexOf(',', commaIndex+1);

String firstValue = myString.substring(0, commaIndex);
String secondValue = myString.substring(commaIndex+1, secondCommaIndex);
String thirdValue = myString.substring(secondCommaIndex); // To the end of the string


***/
