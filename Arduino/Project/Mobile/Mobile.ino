#include "ESP8266.h"
#include "Arduino.h"
#include "Message.h"
#include "Avt.h"

#define SSID            "HONOR_KIW-L21_E44A"
#define PASSWORD        "catalina"

#define SERVER_ADDR     "192.168.43.44"
#define PORT            4000


#define FAILURE         "FAIL"
#define SUCCESS         "SUCCESS"

#define NODE_TYPE       2
#define POS_X           0.0f
#define POS_Y           0.0f

#define TEST            false
#define MAX_ESSAI       5


uint8_t Self_ID = 1;
Mobile mobile = Mobile(Self_ID);
ESP8266 esp;




int iteration = 1;
float minX = 3000;
float maxX = 0;

float minY = 3000;
float maxY = 0;


Vector<Anchor> anchor_List;


void setup(void){
    // Init WIFI
    Serial.begin(9600);
    Serial1.begin(115200);
    esp = ESP8266();
    if(TEST){
        test_init();

    }
    else {
        int i = 0;
        while(i < MAX_ESSAI){
            bool is_connect = init_connection();
            if(is_connect) is_connect =  init_Node();
            if (is_connect) return;
            i++;
        }
        test_init();
    }

}

void loop(void){
  delay(700);
  if (iteration%50 == 0){
      Serial.print("minX :");
      Serial.print(minX);
      Serial.print(" maxX :");
      Serial.println(maxX);


      Serial.print("minY :");
      Serial.print(minY);
      Serial.print(" maxY :");
      Serial.println(maxY);

      minX = 3000;
      maxX = 0;

      minY = 3000;
      maxY = 0;
  }

  if(TEST)test_loop();
  else real_loop();
  //Serial.println(esp.getAPList());
}







void test_loop(){
    mobile.get_chosen_Anchor_I(0)->adjust_Range(141.42+range());

    //Mise a jour du range
    mobile.get_chosen_Anchor_I(1)->adjust_Range(100+range());

    //Mise a jour du range
    mobile.get_chosen_Anchor_I(2)->adjust_Range(100+range());

    Serial.print("------------------------");
    Serial.print(iteration);
    Serial.println("------------------------");

    // Affichage du Range
    for(int i = 0; i < mobile.get_chosen_Anchor().size(); i++){

        Serial.print("Avt range A_");
        Serial.print(mobile.get_chosen_Anchor_I(i)->getId());
        Serial.print(" :");
        Serial.print(mobile.get_chosen_Anchor_I(i)->get_Range());
        Serial.print("\t");
    }
    Serial.println();
    mobile.trilateration();


    if (minX > mobile.getX()) minX = mobile.getX();
    if (maxX < mobile.getX()) maxX = mobile.getX();

    if (minY > mobile.getY()) minY = mobile.getY();
    if (maxY < mobile.getY()) maxY = mobile.getY();

    Serial.print("X :");
    Serial.print(mobile.getX());
    Serial.print(" Y :");
    Serial.println(mobile.getY());
    iteration++;
}

void real_loop(){
    Serial.print("------------------------");
    Serial.print(iteration);
    Serial.println("------------------------");
    for(int i = 0; i < mobile.get_chosen_Anchor().size(); i++){
        send_ask_Distance(esp, mobile.get_chosen_Anchor_I(i), Self_ID);
        recv_Anchor_Distance(esp, mobile.get_chosen_Anchor_I(i));

        Serial.print("Avt range A_");
        Serial.print(mobile.get_chosen_Anchor_I(i)->getId());
        Serial.print(" :");
        Serial.println(mobile.get_chosen_Anchor_I(i)->get_Range());
    }
    mobile.trilateration();
    Serial.print("X :");
    Serial.println(mobile.getX());
    //Serial.print(" : -> ");
    //Serial.println(mobile.getXDir());
    Serial.print("Y :");
    Serial.println(mobile.getY());
    //Serial.print(" : -> ");
    //Serial.println(mobile.getYDir());
    send_Log(esp, mobile, iteration);
    iteration++;
}

void test_init(){
    Vector<Anchor*> anchor_List;

    anchor_List.push_back(new Anchor(1));
    anchor_List[0]->set_Position(0.0, 0.0);
    anchor_List[0]->adjust_Range(141.42);
    Serial.println(anchor_List[0]->get_Range());

    anchor_List.push_back(new Anchor(2));
    anchor_List[1]->set_Position(0.0, 100.0);
    anchor_List[1]->adjust_Range(100.0);

    anchor_List.push_back(new Anchor(3));
    anchor_List[2]->set_Position(100.0, 0.0);
    anchor_List[2]->adjust_Range(100.0);

    mobile = Mobile(4);
    mobile.update_Anchor_Liste(anchor_List);

    randomSeed(analogRead(0));

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
    mobile = Mobile(Self_ID);

    Serial.print("send_ask_Anchor_List : ");
    if(send_ask_Anchor_List(esp, Self_ID)){
        Serial.println(SUCCESS);
    }
    else {
        Serial.println(FAILURE);
        return false;
    }

    Vector<Anchor*> anchor_List;

    anchor_List = recv_Anchor_List(esp);

    for (size_t i = 0; i < anchor_List.size(); i++) {
        Serial.print("send_ask_Position id ");
        Serial.print(anchor_List[i]->getId());
        Serial.print(" :");
        if(send_ask_Position(esp, anchor_List[i], Self_ID)){
            Serial.println(SUCCESS);
        }
        else {
            Serial.println(FAILURE);
            return false;
        }
        Serial.print("recv_Anchor_Position id ");
        Serial.print(anchor_List[i]->getId());
        recv_Anchor_Position(esp, anchor_List[i]);
    }
    mobile.update_Anchor_Liste(anchor_List);

    return true;




}


float range(){
    float rand = random(10);
    if(rand>10/2) return 10-rand;
    return rand;
}
