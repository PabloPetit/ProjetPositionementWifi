#include "Message.h"


uint8_t recv_Id(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    uint8_t type_message = tmp[1];
    if(type_message != SET_ID){
        DEBUG.print("\ntype receive ");
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
    if(type_message != ASK_TY){
        DEBUG.print("\ntype receive ");
        DEBUG.println(type_message);
        DEBUG.print("ASK_TY ");
        DEBUG.println(ASK_TY);
        return false;
    }
    return true;
}

bool recv_Comfirm_Type(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    uint8_t type_message = tmp[1];
    if(type_message != CNF_TY){
        DEBUG.print("\ntype receive ");
        DEBUG.println(type_message);
        DEBUG.print("CNF_TY ");
        DEBUG.println(CNF_TY);
        return false;
    }
    return true;
}

Vector<Anchor*> recv_Anchor_List(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    Vector<Anchor*> anchor_List;
    uint8_t type_message = tmp[1];
    if(type_message != RES_AL){
        DEBUG.print("\ntype receive ");
        DEBUG.println(type_message);
        DEBUG.print("RES_AL ");
        DEBUG.println(RES_AL);
        return anchor_List;
    }
    uint8_t i = 2;
    while (tmp[i] != 0) {
        anchor_List.push_back(new Anchor(tmp[i]));
        i++;
    }
    return anchor_List;
}



void recv_Anchor_Position(Server esp, Anchor *ancre){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    float x;
    uint8_t b[] = {tmp[2], tmp[3], tmp[4], tmp[5]};
    memcpy(&x, &b, sizeof(x));
    float y;
    uint8_t c[] = {tmp[7], tmp[8], tmp[9], tmp[10]};
    memcpy(&y, &c, sizeof(y));
    DEBUG.print("X :")
    DEBUG.println(x);
    DEBUG.print("Y :")
    DEBUG.println(y);
    ancre->set_Position(x, y);
}

void recv_Anchor_Distance(Server esp, Anchor *ancre){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    float f;
    uint8_t b[] = {tmp[2], tmp[3], tmp[4], tmp[5]};
    memcpy(&f, &b, sizeof(f));
    DEBUG.print("Distance receive from :");
    DEBUG.print(ancre->getId());
    DEBUG.print(" = ");
    DEBUG.println(f);
    ancre->adjust_Range(f);
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

bool send_ask_Position(Server esp, Anchor *anchor, uint8_t id){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = SERVER_ID;
    tmp[1] = ASK_PS;
    tmp[2] = anchor->getId();

    return esp.send(tmp, BYTE_SZ);
}


bool send_ask_Distance(Server esp, Anchor *anchor, uint8_t id){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = anchor->getId();
    tmp[1] = ASK_DT;
    tmp[2] = id;

    return esp.send(tmp, BYTE_SZ);
}



bool send_Position(Server esp, float x, float y, uint8_t id){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = id;
    tmp[1] = RES_PS;
    uint8_t x_array[4];
    *((float *)x_array) = x;

    uint8_t y_array[4];
    *((float *)y_array) = y;

    tmp[2] = x_array[0];
    tmp[3] = x_array[1];
    tmp[4] = x_array[2];
    tmp[5] = x_array[3];

    tmp[6] = x_array[0];
    tmp[7] = x_array[1];
    tmp[8] = x_array[2];
    tmp[9] = x_array[3];
    return esp.send(tmp, BYTE_SZ);

}

bool send_Distance(Server esp, float d, uint8_t id){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = id;
    tmp[1] = RES_DT;
    uint8_t d_array[4];
    *((float *)d_array) = d;


    tmp[2] = d_array[0];
    tmp[3] = d_array[1];
    tmp[4] = d_array[2];
    tmp[5] = d_array[3];
    return esp.send(tmp, BYTE_SZ);
}
