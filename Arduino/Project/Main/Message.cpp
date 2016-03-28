#include "Message.h"

int getId(Server esp){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 1000);
    String str = (char*)tmp;
    DEBUG.println(str);
    return 4;
}
