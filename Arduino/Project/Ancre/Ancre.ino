#include "ESP8266.h"
#include "Arduino.h"
#include "Message.h"

#define SSID            "HONOR_KIW-L21_E44A"
#define PASSWORD        "catalina"

#define SERVER_ADDR     "192.168.43.44"
#define PORT            4002


#define FAILURE         "FAIL"
#define SUCCESS         "SUCCESS"

#define NODE_TYPE       1
#define POS_X           0.0f
#define POS_Y           0.0f

#define TEST            true


bool cnftype = false;
bool setup_OK = false;
uint8_t Self_ID;
ESP8266 esp;


void setup(void){
    // Init WIFI
    Serial.begin(9600);
    Serial1.begin(115200);
    esp = ESP8266();
    bool is_connect = init_connection();
    if(is_connect) init_Node();

}

void loop(void){
  delay(10);
  real_loop();
}

void real_loop(){
    uint8_t tmp[BYTE_SZ];
    int size = esp.recv(tmp, BYTE_SZ, 2000);

    if(size < MSG_SZ) return;
    uint8_t id = tmp[2];
    uint8_t code = tmp[1];

    switch (code) {
        case ASK_TY://ok
            send_Type_Node(esp, NODE_TYPE);
            break;
        case CNF_TY: // ok
            if(recv_Comfirm_Type(esp))
                cnftype = true;

            break;
        case ASK_DT:
            send_Distance(esp, get_Distance(), id);
            break;
        case ASK_PS:
            send_Position(esp, POS_X, POS_Y, id);
            break;
    }
}


// TODO : ultraSOUND
float get_Distance(){
    if(TEST) return 100.0f;
    else {
        return 100.0f;
    }
}


bool init_connection(){
    // connect to AP
    Serial.print("Connexion ....");

    if(!esp.joinAP(SSID, PASSWORD)){
        Serial.print(FAILURE);
        Serial.print(" to connect AP : ");
        Serial.println(SSID);
        return false;
    }

    // Create TCP
    if(!esp.createTCP(SERVER_ADDR, PORT)){
        Serial.println(FAILURE);
        Serial.print(" to connect TCP Server :");
        Serial.print(SERVER_ADDR);
        Serial.print(" ");
        Serial.println(PORT);
        return false;
    }
    Serial.print(SUCCESS);
    return true;
}

bool init_Node(){
    // getID
    Serial.print("Node ID : ");
    Self_ID = recv_Id(esp);
    Serial.println(Self_ID);

    // confirm ID
    Serial.print("ID confirm : ");
    if(send_Confirm_Id(esp)){
        Serial.println(SUCCESS);
    }
    else {
        Serial.println(FAILURE);
        return false;
    }

    // recoi demande type node
    Serial.print("Receive ask Node Type : ");
    if(recv_Ask_Node_Type(esp)){
        Serial.println(SUCCESS);
    }
    else {
        Serial.println(FAILURE);
        return false;
    }

    // Envoi type node
    Serial.print("Send Node type : ");
    if(send_Type_Node(esp, NODE_TYPE)){
        Serial.println(SUCCESS);
    }
    else {
        Serial.println(FAILURE);
        return false;
    }

    Serial.print("recv Confirm Node type : ");
    while(true){
        if(recv_Comfirm_Type(esp)){
            Serial.println(SUCCESS);
            break;
        }
        else {
            Serial.println(FAILURE);

        }
    }
    return true;
}




float range(){
    float rand = random(10);
    if(rand>10/2) return 10-rand;
    return rand;
}
