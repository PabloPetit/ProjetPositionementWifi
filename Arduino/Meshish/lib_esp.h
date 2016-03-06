#ifndef __LIB_ESP__
#define __LIB_ESP__

#include <Arduino.h>
#define TIMEOUT 10000
#define ESP8266 Serial1


bool eps_restart(void);

bool eps_AT(void);

void rx_empty(void);

bool recvFind(String target);

String recvString(String target);

String recvString2(String target, String target2);

bool esp_set_wifi_mode_both(void);

bool esp_ask_wifi_mode(uint8_t *mode);

bool esp_set_wifi_mode(uint8_t mode);

bool recvFindAndFilter(String target, String begin, String end, String &data);

bool esp_join_Access_Point(String ssid, String pwd);

String esp_get_local_IP(void);

String esp_get_Joined_Device_IP(void);

bool esp_set_Access_Point_Parameters(String ssid, String pwd, uint8_t chl, uint8_t ecn);

bool quit_AP(void);

String getAPList(void);

String getIPStatus(void);

int getIPStatusInt(void);

bool qCWJAP();

String esp_get_formated_local_IP();


#endif /* #ifndef __LIB_ESP__ */
