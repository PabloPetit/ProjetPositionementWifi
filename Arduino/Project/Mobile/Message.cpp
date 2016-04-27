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
        return 0; // ne correspond pas à un id possible
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
    uint8_t nb_anchor = tmp[2];
    DEBUG.print("Nombre d'ancre :");
    DEBUG.println(nb_anchor);
    uint8_t i = 3;
    while (tmp[i] != 0) {
        DEBUG.println(tmp[i]);
        anchor_List.push_back(new Anchor(tmp[i]));
        i++;
    }
    if (i-3 != nb_anchor){
        DEBUG.println("Erreur sur ne nombre d'ancre recu :");
        DEBUG.print("Attendu ");
        DEBUG.println(nb_anchor);
        DEBUG.print("Recu ");
        DEBUG.println(i-3);
    }

    return anchor_List;
}



int recv_Anchor_Position(Server esp, Anchor *ancre){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    uint8_t type_message = tmp[1];
    if(type_message != RES_PS){
        DEBUG.print("\ntype receive ");
        DEBUG.println(type_message);
        DEBUG.print("RES_PS ");
        DEBUG.println(RES_PS);
        return -1;
    }


    float x;
    uint8_t b[] = {tmp[2], tmp[3], tmp[4], tmp[5]};
    memcpy(&x, &b, sizeof(x));
    float y;
    uint8_t c[] = {tmp[6], tmp[7], tmp[8], tmp[9]};
    memcpy(&y, &c, sizeof(y));
    DEBUG.print("X :");
    DEBUG.print(x);
    DEBUG.print(" Y :");
    DEBUG.println(y);
    ancre->set_Position(x, y);
    return 1;
}

float recv_Anchor_Distance(Server esp, Anchor *ancre){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);
    uint8_t type_message = tmp[1];
    if(type_message != RES_DT){
        DEBUG.print("\ntype receive ");
        DEBUG.println(type_message);
        DEBUG.print("RES_DT ");
        DEBUG.println(RES_DT);
        return -1.0f;
    }


    float f;
    uint8_t b[] = {tmp[2], tmp[3], tmp[4], tmp[5]};
    memcpy(&f, &b, sizeof(f));
    DEBUG.print("Distance receive from :");
    DEBUG.print(ancre->getId());
    DEBUG.print(" = ");
    DEBUG.println(f);
    ancre->adjust_Range(f);
    return f;
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
    tmp[0] = anchor->getId();
    tmp[1] = ASK_PS;
    tmp[2] = id;

    return esp.send(tmp, BYTE_SZ);
}


bool send_ask_Distance(Server esp, Anchor *anchor, uint8_t id){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = anchor->getId();
    tmp[1] = ASK_DT;
    tmp[2] = id;

    return esp.send(tmp, BYTE_SZ);
}

bool send_Log(Server esp, Mobile mobile, int iteration, float d1, float d2, float d3){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = SERVER_ID;
    tmp[1] = RES_LG;
    uint8_t x_array[4];
    *((float *)x_array) = mobile.getX();
    tmp[2] = x_array[0];
    tmp[3] = x_array[1];
    tmp[4] = x_array[2];
    tmp[5] = x_array[3];

    *((float *)x_array) = mobile.getY();
    tmp[6] = x_array[0];
    tmp[7] = x_array[1];
    tmp[8] = x_array[2];
    tmp[9] = x_array[3];

    *((float *)x_array) = mobile.get_chosen_Anchor_I(0)->get_Range();
    tmp[10] = x_array[0];
    tmp[11] = x_array[1];
    tmp[12] = x_array[2];
    tmp[13] = x_array[3];

    *((float *)x_array) = d1;
    tmp[14] = x_array[0];
    tmp[15] = x_array[1];
    tmp[16] = x_array[2];
    tmp[17] = x_array[3];

    *((float *)x_array) = mobile.get_chosen_Anchor_I(1)->get_Range();
    tmp[18] = x_array[0];
    tmp[19] = x_array[1];
    tmp[20] = x_array[2];
    tmp[21] = x_array[3];

    *((float *)x_array) = d2;
    tmp[22] = x_array[0];
    tmp[23] = x_array[1];
    tmp[24] = x_array[2];
    tmp[25] = x_array[3];

    *((float *)x_array) = mobile.get_chosen_Anchor_I(2)->get_Range();
    tmp[26] = x_array[0];
    tmp[27] = x_array[1];
    tmp[28] = x_array[2];
    tmp[29] = x_array[3];

    *((float *)x_array) = d3;
    tmp[30] = x_array[0];
    tmp[31] = x_array[1];
    tmp[32] = x_array[2];
    tmp[33] = x_array[3];

    *((float *)x_array) = (float) iteration;
    tmp[34] = x_array[0];
    tmp[35] = x_array[1];
    tmp[36] = x_array[2];
    tmp[37] = x_array[3];

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


bool send_IMOUT(Server esp, uint8_t id){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = id;
    tmp[1] = IM_OUT;
    return esp.send(tmp, BYTE_SZ);
}
