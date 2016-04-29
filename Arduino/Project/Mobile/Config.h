#ifndef __CONFIG_H__
#define __CONFIG_H__
#include "Arduino.h"
/**
 * Ce fichier
 *
 *
 */


//#define SSID            "HONOR_KIW-L21_E44A"
//#define PASSWORD        "catalina"
//#define SERVER_ADDR     "192.168.43.7"
#define SSID            "NETGEAR"
#define PASSWORD        ""
#define SERVER_ADDR     "192.168.0.4"


#define PORT            4000
#define FAILURE         "FAIL"
#define SUCCESS         "SUCCESS"

#define MAX_ESSAI       5
#define MODE_DEBUG      false
#define DELAI           0 // delai entre les demande d'evaluation de distance


#define ANCRE           1
#define MOBILE          2
#define NODE_TYPE       MOBILE


#define POS_X           0.0f
#define POS_Y           0.0f
#define echoPin 7
#define trigPin 8

#define LOG_PRINTLN(arg)\
    if (MODE_DEBUG)\
        Serial.println(arg);

#define LOG_PRINT(arg)\
    if (MODE_DEBUG)\
        Serial.print(arg);


/**
 * Initialistation
 */
bool init_connection();

bool config_Node();
bool init_Node();
void l_Ancre();
float get_Distance();
void mobile_lloopp();


#endif
