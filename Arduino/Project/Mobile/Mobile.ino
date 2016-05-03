#include "ESP8266.h"
#include "Message.h"
#include "Config.h"


int iteration       = 1;
bool cnftype        = false;
int nb = 1;
unsigned long start;

uint8_t Self_ID;
Mobile mobile;
ESP8266 esp;






void setup(void){
    // Init Serial port & ESP
    Serial.begin(9600);
    Serial1.begin(115200);
    esp = ESP8266();
    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);


    int i = 0;
    while(i < MAX_ESSAI){
        bool is_connect = init_connection();
        if(is_connect) is_connect =  init_Node();
        if (is_connect) return;
        i++;
    }

}

void loop(void){
    if(NODE_TYPE == ANCRE) l_Ancre();
    else mobile_lloopp();
}

bool init_connection(){
    // connect to AP
    LOG_PRINT("Connexion ....");

    if(!esp.joinAP(SSID, PASSWORD)){
        LOG_PRINT(FAILURE);
        LOG_PRINT(" to connect AP : ");
        LOG_PRINTLN(SSID);
        return false;
    }

    // Create TCP
    if(!esp.createTCP(SERVER_ADDR, PORT)){
        LOG_PRINTLN(FAILURE);
        LOG_PRINT(" to connect TCP Server :");
        LOG_PRINT(SERVER_ADDR);
        LOG_PRINT(" ");
        LOG_PRINTLN(PORT);
        return false;
    }
    LOG_PRINT(SUCCESS);
    return true;
}

bool config_Node(){
    // getID
    LOG_PRINT("Node ID : ");
    Self_ID = recv_Id(esp);
    LOG_PRINTLN(Self_ID);

    // confirm ID
    LOG_PRINT("ID confirm : ");
    if(send_Confirm_Id(esp)){
        LOG_PRINTLN(SUCCESS);
    }
    else {
        LOG_PRINTLN(FAILURE);
        return false;
    }

    // recoi demande type node
    LOG_PRINT("Receive ask Node Type : ");
    if(recv_Ask_Node_Type(esp)){
        LOG_PRINTLN(SUCCESS);
    }
    else {
        LOG_PRINTLN(FAILURE);
        return false;
    }

    // Envoi type node
    LOG_PRINT("Send Node type : ");
    if(send_Type_Node(esp, NODE_TYPE)){
        LOG_PRINTLN(SUCCESS);
    }
    else {
        LOG_PRINTLN(FAILURE);
        return false;
    }
    LOG_PRINT("recv Confirm Node type : ");
    while(true){
        if(recv_Comfirm_Type(esp)){
            LOG_PRINTLN(SUCCESS);
            break;
        }
        else {
            LOG_PRINTLN(FAILURE);

        }
    }
}

bool init_Node(){
    bool config = config_Node();
    if(!config) return false;

    // si on est une ancre la configuration est terminé
    if(NODE_TYPE == ANCRE) return true;
    mobile = Mobile(Self_ID);
    start = millis();
    return true;
}

void l_Ancre(){
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
        case ASK_ST:
            send_Status(esp, POS_X, POS_Y, get_Distance(), id);
            break;
    }
}
// TODO : Test
float get_Distance(){

    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    float t = pulseIn(echoPin, HIGH);
    return t/2.0f/29.0f;
}

void mobile_lloopp(){

    float distances[3]  = {0.0f, 0.0f, 0.0f};
    delay(DELAI);
    Serial.println("0000000000@@@@@@@@@@@@@@@@@@@@@@@@@@@@###############");
    Serial.println("0000000000@@@@@@@@@@@@@@@@@@@@@@@@@@@@###############");
    Serial.println("0000000000@@@@@@@@@@@@@@@@@@@@@@@@@@@@###############");
    Serial.println("0000000000@@@@@@@@@@@@@@@@@@@@@@@@@@@@###############");
    Serial.print("------------------------");
    Serial.print(iteration);
    Serial.println("------------------------");
    if(mobile.get_anchor_size() < 3){
        LOG_PRINTLN("moins de 3 ancres ");
        Vector<Anchor*> anchor_List;
        LOG_PRINT("send_ask_Anchor_List : ");
        if(send_ask_Anchor_List(esp, Self_ID)){
            LOG_PRINTLN(SUCCESS);
        }
        else {
            LOG_PRINTLN(FAILURE);
            return;
        }
        anchor_List = recv_Anchor_List(esp);


        mobile.update_Anchor_Liste(anchor_List);
    }

    int active = 0;
    for(int i = 0; i < mobile.get_anchor_size(); i++){
        delay(300);
        LOG_PRINT("send_ask_Status ");
        LOG_PRINTLN(mobile.get_Anchor(i)->getId());
        if(send_ask_Status(esp, mobile.get_Anchor(i), Self_ID)){
            LOG_PRINTLN(SUCCESS);
        }
        else {
            LOG_PRINTLN(FAILURE);
            return;
        }
        LOG_PRINT("recv_Anchor_status id ");
        LOG_PRINT(mobile.get_Anchor(i)->getId());
        distances[active] = recv_Anchor_Status(esp, mobile.get_Anchor(i));
        if((distances[active]) > 1 ){
            active++;
            LOG_PRINTLN(mobile.get_Anchor(i)->get_Range());
            if(active == 3) break;

        }
        else{
            mobile.remove_Anchor_Id(mobile.get_Anchor(i)->getId());
            LOG_PRINTLN(FAILURE);
        }

    }

    if(active == 3){
        mobile.trilateration();
        Serial.print("X :");
        Serial.print(mobile.getX());
        Serial.print(" Y :");
        Serial.println(mobile.getY());
        send_Log(esp, mobile, iteration, distances[0], distances[1], distances[2], 0);
        iteration++;
        nb++;
    }

}
