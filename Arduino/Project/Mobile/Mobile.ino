#include "ESP8266.h"
#include "Arduino.h"
#include "Message.h"
#include "Avt.h"

#define SSID        "HONOR_KIW-L21_E44A"


#define PASSWORD    "catalina"

#define SERVER_ADDR "192.168.43.44"
#define PORT        4002
#define NODE_TYPE 2


#define FAILURE "FAILURE"
#define SUCCESS "SUCCESS"



uint8_t Self_ID;

bool isHost = false;
ESP8266 esp;

Vector<Anchor> anchor_List;

void setup(void){
    // Init WIFI
    Serial.begin(9600);
    Serial1.begin(115200);
    esp = ESP8266();
    Vector<Anchor> anchor_List;
    anchor_List.push_back(Anchor(1));

    anchor_List[0].set_Position(4.0, 4.0);
    anchor_List[0].set_Range(4.0);

    anchor_List.push_back(Anchor(2));
    anchor_List[1].set_Position(9.0, 7.0);
    anchor_List[1].set_Range(3.0);

    anchor_List.push_back(Anchor(3));
    anchor_List[2].set_Position(9.0, 1.0);
    anchor_List[2].set_Range(3.25);

    Mobile mobile = Mobile(4);


    mobile = trilateration(anchor_List, mobile);
    Serial.print("X :");
    Serial.println(mobile.getX());
    Serial.print("Y :");
    Serial.println(mobile.getY());

    /*bool init = init_Client();

    Serial.print("send_ask_Anchor_List : ");
    if(send_ask_Anchor_List(esp, Self_ID)){
        Serial.println(SUCCESS);
    }
    anchor_List = recv_Anchor_List(esp);

    for (size_t i = 0; i < anchor_List.size(); i++) {

        send_ask_Position(esp, anchor_List[i], Self_ID);
        recv_Anchor_Position(esp, anchor_List[i]);

        send_ask_Distance(esp, anchor_List[i], Self_ID);
        recv_Anchor_Distance(esp, anchor_List[i]);


    }

    */




    /**
    * SETUP:
    * X Connect to AP
    * X Connect to server (TCP)
    * X Recuperer la liste des ancres
    * - Recuperer les positions des ancres
    *
    * LOOP:
    * - get range evalualtion
    * -
    */


}

void loop(void){
  delay(100);
  //Serial.println(esp.getAPList());
}


bool init_Client(){
    // connect to AP
    Serial.print("Connect to l'AP :");
    Serial.println(SSID);
    if(esp.joinAP(SSID, PASSWORD)){
        Serial.println(SUCCESS);
    }
    else {
        Serial.println(FAILURE);
        return false;
    }

    // Create TCP
    Serial.print("Connect to TCP Server :");
    Serial.print(SERVER_ADDR);
    Serial.print(" ");
    Serial.println(PORT);
    if(esp.createTCP(SERVER_ADDR, PORT)){
        Serial.println(SUCCESS);
    }
    else {
        Serial.println(FAILURE);
        return false;
    }

    // getID
    Serial.print("Receive Node ID : ");
    Self_ID = recv_Id(esp);
    Serial.println(Self_ID);

    // confirm ID
    Serial.print("Send confirm ID : ");
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
