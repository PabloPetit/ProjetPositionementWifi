#include "Message.h"


int recv_Id(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 1000);
    String str = (char*)tmp;
    char type[2] = {0};
    str = str.substring(1,2);
    str.toCharArray(type, 2);
    if(atoi(type) != 0){
        return -1;
    }
    str = str.substring(2, str.indexOf('#'));
    int myStringLength = str.length()+1;
    char myChar[myStringLength];
    str.toCharArray(myChar,myStringLength);
    return atoi(myChar);
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

bool send_Confirm_Id(Server esp){
    char *hello = "011############################";
    return esp.send((const uint8_t*)hello, strlen(hello));
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
