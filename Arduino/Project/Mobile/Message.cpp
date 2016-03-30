#include "Message.h"


int recv_Id(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 1000);

    uint8_t type_message = tmp[1];
    DEBUG.print("type message :");
    DEBUG.println(type_message);
    if(type_message != SET_ID){
        return -1;
    }
    uint8_t id_Node = tmp[2];
    DEBUG.print("id node :");
    DEBUG.println(id_Node);
    return id_Node;



    /*String str = (char*)tmp;
    DEBUG.println(str);
    char type[2] = {0};
    String s = str.substring(1,2);
    s.toCharArray(type, 2);
    if(atoi(type) != 0){
        return -1;
    }
    str = str.substring(2, str.indexOf('#'));

    int myStringLength = str.length()+1;
    char myChar[myStringLength];
    str.toCharArray(myChar,myStringLength);
    return atoi(myChar);*/
}


bool recv_Ask_Node_Type(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 1000);
    String str = (char*)tmp;
    char type[2] = {0};
    str = str.substring(1,2);
    str.toCharArray(type, 2);
    if(atoi(type) != 2){
        return false;
    }
    return true;
}


Vector<Anchor> recv_Anchor_List(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 1000);
    String str = (char*)tmp;
    str = str.substring(2, str.indexOf('#'));
    Vector<Anchor> anchor_List;
    DEBUG.println(str);
    int i = 0;
    for (size_t i = 0; i < str.length(); i++) {
        String s;
        char type[3] = {0};
        s = str.substring(i,i+1);
        s.toCharArray(type, 2);
        anchor_List.push_back(Anchor(atoi(type)));
    }
    return anchor_List;
}



Anchor recv_Anchor_Position(Server esp, Anchor ancre){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 1000);
    String str = (char*)tmp;
    DEBUG.println(str);
    return ancre;
}




















bool send_Confirm_Id(Server esp){
    uint8_t tmp[BYTE_SZ] = {0};
    tmp[0] = SERVER_ID;
    tmp[1] = CNF_ID;
    return esp.send(tmp, BYTE_SZ);
    /*
    char *hello = "011############################";
    return esp.send((const uint8_t*)hello, strlen(hello));
    */
}


bool send_Type_Node(Server esp, int node_type){
    char *hello;
    if (node_type == 1){
        hello = "031############################";
    }
    else {
        hello = "030############################";
    }

    return esp.send((const uint8_t*)hello, strlen(hello));
}

bool send_ask_Anchor_List(Server esp){
    char * hello = "044############################";


    return esp.send((const uint8_t*)hello, strlen(hello));

}

bool send_ask_Position(Server esp, Anchor anchor, int id){
    String sid = String(id, DEC);
    String stype = String(ASK_PS, DEC);
    String said = String(anchor.getId(), DEC);
    String final = said + stype +  sid;

    for (size_t i = final.length(); i < BYTE_SZ; i++) {
        final += '#';
    }
    char hello[BYTE_SZ] = {0};
    final.toCharArray(hello, final.length());
    return esp.send((const uint8_t*)hello, strlen(hello));
}

Anchor recv_Anchor_List(Server esp, Anchor ancre){

}
