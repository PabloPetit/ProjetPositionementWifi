#ifndef __MESSAGE_H__
#define __MESSAGE_H__

#include "ESP8266.h"
#include "Anchor.h"
#include "Vector.h"

#define Server ESP8266

#define SERVER_ID 1
#define MSG_SZ 64
#define MSG_LN 62

#define BYTE_SZ 64


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
#define UNK_ID  13       // Id inconnue, message non redirigé : MESS = dest
#define IM_OUT  14       // Annonce une sortie du réseau TODO
#define RES_LG  15       // Fichier de log MESS = CRT_X + CRT_Y + CRT_DT_1 + CRT_DT_2 + CRT_DT_3 + IT

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
Vector<Anchor*> recv_Anchor_List(Server esp);


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
 * @return
 */
int recv_Anchor_Position(Server esp, Anchor *ancre);

/**
 * Récupère La distance d'une ancre
 *
 * @param esp - module wifi esp8266 pour la communication
 * @return
 */
float recv_Anchor_Distance(Server esp, Anchor *ancre);



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
 * 2 = Mobile
 * 1 = Ancre
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
bool send_ask_Position(Server esp, Anchor *anchor, uint8_t id);



/**
 * Envoi au serveur une demande d'évaluation de la distance
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_ask_Distance(Server esp, Anchor *anchor, uint8_t id);









/**
 * Envoi au serveur le log de l'iteration
 *
 * Les donné envoyé sont notre avt_x avt_y et les trois avts des ancres
 *
 * @param esp - module wifi esp8266 pour la communication
 * @param iteration - numero de l'iteration
 * @retval true - success.
 * @retval false - failure.
 */
bool send_Log(Server esp, Mobile mobile, int iteration, float d1, float d2, float d3);


/**
 * Envoi au serveur notre position
 *
 * @param esp - module wifi esp8266 pour la communication
 * @param X - notre position X
 * @param Y - notre position Y
 * @retval true - success.
 * @retval false - failure.
 */
bool send_Position(Server esp, float x, float y, uint8_t id);


/**
 * Envoi au serveur une evaluation de distance
 *
 * @param esp - module wifi esp8266 pour la communication
 * @param d - distance evalué
 * @retval true - success.
 * @retval false - failure.
 */
bool send_Distance(Server esp, float d, uint8_t id);


/**
 * Envoi au serveur une notification de sortie du reseau
 *
 * @param esp - module wifi esp8266 pour la communication
 * @retval true - success.
 * @retval false - failure.
 */
bool send_IMOUT(Server esp, uint8_t id);

#endif
