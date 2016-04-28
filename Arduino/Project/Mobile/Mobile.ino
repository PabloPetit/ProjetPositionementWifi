#include "ESP8266.h"
#include "Arduino.h"
#include "Message.h"
#include "Avt.h"
#include "Config.h"


uint8_t Self_ID = 0;
Mobile mobile = Mobile(Self_ID);
ESP8266 esp;
int iteration = 1;
Vector<Anchor> anchor_List;
bool cnftype = false;
bool setup_OK = false;
float distances[3] = {0.0f,0.0f,0.0f};


bool init_connection();
bool config_Node();
bool init_Node();
void l_Ancre();
//void l_Mobile();
float get_Distance();
//Vector<Anchor*> get_anchor_list();
void mobile_lloopp();




void setup(void){
    // Init Serial port & ESP
    int a = 10/0;

    Serial.begin(9600);
    Serial1.begin(115200);

    LOG_PRINTLN(a);
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

    /*Vector<Anchor*> anchor_List;
    do{
        anchor_List = get_anchor_list();
        if(anchor_List.size()< 3)delay(DELAI);
    }while(anchor_List.size() < 3);

    mobile.update_Anchor_Liste(anchor_List);*/

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

/*void l_Mobile(){
    // delai entre les itération de l'algo
    delay(DELAI);


    LOG_PRINT("------------------------");
    LOG_PRINT(iteration);
    LOG_PRINTLN("------------------------");

    for(int i = 0; i < mobile.get_chosen_Anchor().size(); i++){
        delay(150);
        send_ask_Distance(esp, mobile.get_chosen_Anchor_I(i), Self_ID);
        distances[i] =  recv_Anchor_Distance(esp, mobile.get_chosen_Anchor_I(i));

        if(distances[i] < 0){
            LOG_PRINT("Ask distance : ");
            LOG_PRINTLN(FAILURE);
        }


        LOG_PRINT("Avt range A_");
        LOG_PRINT(mobile.get_chosen_Anchor_I(i)->getId());
        LOG_PRINT(" :");
        LOG_PRINTLN(mobile.get_chosen_Anchor_I(i)->get_Range());
    }


    mobile.trilateration();


    LOG_PRINT("X :");
    LOG_PRINTLN(mobile.getX());
    LOG_PRINT("Y :");
    LOG_PRINTLN(mobile.getY());


    Envoi du log au serveur

    send_Log(esp, mobile, iteration, distances[0], distances[1], distances[2]);
    iteration++;
}*/

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

/*Vector<Anchor*> get_anchor_list(){
        Vector<Anchor*> anchor_List, nul;
        LOG_PRINT("send_ask_Anchor_List : ");
        if(send_ask_Anchor_List(esp, Self_ID)){
            LOG_PRINTLN(SUCCESS);
        }
        else {
            LOG_PRINTLN(FAILURE);
            return anchor_List;
        }



        anchor_List = recv_Anchor_List(esp);

        for (size_t i = 0; i < anchor_List.size(); i++) {
            LOG_PRINT("send_ask_Position id ");
            LOG_PRINT(anchor_List[i]->getId());
            LOG_PRINT(" :");

            if(send_ask_Position(esp, anchor_List[i], Self_ID)){
                LOG_PRINTLN(SUCCESS);
            }
            else {
                LOG_PRINTLN(FAILURE);
                return nul;
            }
            LOG_PRsend_Log(esp, mobile, iteration, distances[0], distances[1], distances[2]);INT("recv_Anchor_Position id ");
            LOG_PRINT(anchor_List[i]->getId());

            if(recv_Anchor_Position(esp, anchor_List[i]) < 1 ){
                LOG_PRINTLN(FAILURE);
                return nul;
            }
        }
        return anchor_List;
}*/








































void mobile_lloopp(){

    delay(DELAI);
    if(iteration%60 == 0){
        LOG_PRINTLN("------------------------");
        LOG_PRINTLN("------------------------");
        LOG_PRINTLN("KILL ANCRE !!!!");
        LOG_PRINTLN("------------------------");
        LOG_PRINTLN("------------------------");
        delay(30000);
     }

    LOG_PRINT("------------------------");
    LOG_PRINT(iteration);
    LOG_PRINTLN("------------------------");
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
        delay(250);
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
        if((distances[active]) > 0 ){
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
        LOG_PRINT("X :");
        LOG_PRINTLN(mobile.getX());
        LOG_PRINT("Y :");
        LOG_PRINTLN(mobile.getY());
        send_Log(esp, mobile, iteration, distances[0], distances[1], distances[2]);
        iteration++;
    }

}
