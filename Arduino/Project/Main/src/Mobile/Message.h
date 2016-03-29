#ifndef __MESSAGE_H__
#define __MESSAGE_H__

#include "ESP8266.h"
#include "Anchor.h"
#include "Vector.h"

#define Server ESP8266


#define MSG_SZ 32
#define MSG_LN 30

#define BYTE_SZ 65


//RECEPTION
#define SET_ID 0
#define RES_TY 3
#define RES_AL 5
#define RES_DT 7
#define RES_PS 9

//ENVOI
#define CNF_ID 1
#define ASK_TY 2
#define ASK_AL 4
#define ASK_DT 6
#define ASK_PS 8

// ENVOI


/**
 * Récupère l'id que le serveur nous a attribué
 *
 * @param esp - module wifi esp8266 pour la communication
 * @return l'id reçu
 */
int recv_Id(Server esp);


/**
 * Récupère une demande de type de Node
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - Le message a bien été reçu.
 * @retval false - pas de demande.
 */
bool recv_Ask_Node_Type(Server esp);

/**
 * Récupère La liste des ancres
 *
 * @param esp - module wifi esp8266 pour la communication
 * @return Vector<Anchor> liste des ancres
 */
Vector<Anchor> recv_Anchor_List(Server esp);


/**
 * Récupère La position d'une ancre
 *
 * @param esp - module wifi esp8266 pour la communication
 * @return Ancre liste des ancres
 */
Anchor recv_Anchor_Position(Server esp, Anchor ancre);



// RECEPTION
/**
 * Envoi au serveur une confirmation que l'on a bien reçu notre ID
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_Confirm_Id(Server esp);


/**
 * Envoi au serveur une confirmation de notre Type
 * 1 = Mobile
 * 0 = Ancre
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_Type_Node(Server esp, int node_type);

/**
 * Envoi au serveur une demande de la liste des ancres
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_ask_Anchor_List(Server esp);


/**
 * Envoi au serveur une demande de la position d'une ancre
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_ask_Position(Server esp, Anchor anchor, int id);


#endif
