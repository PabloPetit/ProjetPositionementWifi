#ifndef __MESSAGE_H__
#define __MESSAGE_H__

#include "ESP8266.h"
#include "Anchor.h"
#include "Vector.h"

#define Server ESP8266

#define SERVER_ID 1
#define MSG_SZ 32
#define MSG_LN 30

#define BYTE_SZ 65


#define SET_ID  1        // Donne son id à un noeud : MESS = id
#define CNF_ID  2        // Confirme la reception de l'id : MESS = NULL
#define ASK_TY  3        // Demande le type d'un noeud : MESS = id
#define RES_TY  4        // Donne son type  : MESS = A | M
#define CNF_TY  5        // Confirme la reception du type
#define ASK_AL  6        // Demande la liste des ancres : MESS = id
#define RES_AL  7        // Donne la liste des ancres : MESS = int + id*
#define ASK_DT  8        // Demande une evaluation de distance : MESS = id
#define RES_DT  9        // Renvoi l'evaluation de distance : MESS = int
#define ASK_PS  10       // Demande sa position à une ancre : MESS = id
#define RES_PS  11       // Renvoi sa position : MESS = int+int
#define ASK_ID  12       // Redemande son id
#define UNK_ID  13       //Id inconnue, message non redirigé : MESS = dest


// ENVOI


/**
 * Récupère l'id que le serveur nous a attribué
 *
 * @param esp - module wifi esp8266 pour la communication
 * @return l'id reçu
 */
uint8_t recv_Id(Server esp);


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
 * Récupère la confirmation du serveur sur notre type
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true confirmation correct
 * @retval false
 */
bool recv_Comfirm_Type(Server esp);


/**
 * Récupère La position d'une ancre
 *
 * @param esp - module wifi esp8266 pour la communication
 * @return Ancre liste des ancres
 */
Anchor recv_Anchor_Position(Server esp, Anchor ancre);

/**
 * Récupère La position d'une ancre
 *
 * @param esp - module wifi esp8266 pour la communication
 * @return Ancre liste des ancres
 */
Anchor recv_Anchor_Distance(Server esp, Anchor ancre);



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
bool send_Type_Node(Server esp, uint8_t node_type);

/**
 * Envoi au serveur une demande de la liste des ancres
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_ask_Anchor_List(Server esp, uint8_t id);


/**
 * Envoi au serveur une demande de la position d'une ancre
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_ask_Position(Server esp, Anchor anchor, uint8_t id);



/**
 * Envoi au serveur une demande de la position d'une ancre
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_ask_Distance(Server esp, Anchor anchor, uint8_t id);

#endif
