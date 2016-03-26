#ifndef __MESSAGE_H__
#define __MESSAGE_H__

#include "ESP8266.h"

#define Server ESP8266


#define MSG_SZ 32
#define MSG_LN 30

//RECEPTION
#define SET_ID 0 // Donne son id à un noeud : MESS = id
#define RES_TY 3 // Donne son type  : MESS = A | M
#define RES_AL 5 // Donne la liste des ancres : MESS = int + id*
#define RES_DT 7 // Renvoi l'evaluation de distance : MESS = int
#define RES_PS 9 // Renvoi sa position : MESS = int+int

//ENVOI
#define CNF_ID 1 // Confirme la reception de l'id : MESS = NULL
#define ASK_TY 2 // Demande le type d'un noeud : MESS = id
#define ASK_AL 4 // Demande la liste des ancres : MESS = id
#define ASK_DT 6 // Demande une evaluation de distance : MESS = id
#define ASK_PS 8 // Demande sa position à une ancre : MESS = id

// ENVOI
// renvoi l'id du client
int getId(Server esp);

int get_Node_Type(Server esp, Anchor anchor);



// RECEPTION
//envoi un message au server
bool confirm_Id(Server esp, Client client);






#endif
