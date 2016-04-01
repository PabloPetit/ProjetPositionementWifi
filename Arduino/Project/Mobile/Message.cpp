#include "Message.h"


uint8_t recv_Id(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);

    DEBUG.print("taille ");
    DEBUG.println(size);
    uint8_t type_message = tmp[1];
    if(type_message != SET_ID){
        DEBUG.print("type_message ");
        DEBUG.println(type_message);
        DEBUG.print("SET_ID ");
        DEBUG.println(SET_ID);
        return -1;
    }
    uint8_t id_Node = tmp[2];
    return id_Node;
}


bool recv_Ask_Node_Type(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);

    uint8_t type_message = tmp[1];
    DEBUG.print("type_message ");
    DEBUG.println(type_message);
    if(type_message != ASK_TY){
        return false;
    }
    return true;
}

bool recv_Comfirm_Type(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);

    uint8_t type_message = tmp[1];
    if(type_message != CNF_TY){
        DEBUG.print("type_message ");
        DEBUG.println(type_message);
        DEBUG.print("CNF_TY ");
        DEBUG.println(CNF_TY);
        return false;
    }
    return true;
}

Vector<Anchor> recv_Anchor_List(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    String str = (char*)tmp;
    DEBUG.println(str);
    Vector<Anchor> anchor_List;
    uint8_t type_message = tmp[1];
    if(type_message != RES_AL){
        DEBUG.print("type_message ");
        DEBUG.println(type_message);
        DEBUG.print("RES_AL ");
        DEBUG.println(RES_AL);
        return anchor_List;
    }
    uint8_t i = 2;
    while (tmp[i] != 0) {
        anchor_List.push_back(Anchor(tmp[i]));
        i++;
    }
    return anchor_List;
}



Anchor recv_Anchor_Position(Server esp, Anchor ancre){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    String str = (char*)tmp;
    DEBUG.println(str);
    return ancre;
}




















bool send_Confirm_Id(Server esp){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = SERVER_ID;
    tmp[1] = CNF_ID;
    return esp.send(tmp, BYTE_SZ);
}


bool send_Type_Node(Server esp, uint8_t node_type){

    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = SERVER_ID;
    tmp[1] = RES_TY;
    tmp[2] = node_type;
    return esp.send(tmp, BYTE_SZ);
}

bool send_ask_Anchor_List(Server esp, uint8_t id){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = SERVER_ID;
    tmp[1] = ASK_AL;
    tmp[2] = id;
    return esp.send(tmp, BYTE_SZ);

}

bool send_ask_Position(Server esp, Anchor anchor, uint8_t id){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = SERVER_ID;
    tmp[1] = ASK_PS;
    tmp[2] = anchor.getId();

    return esp.send(tmp, BYTE_SZ);



}
