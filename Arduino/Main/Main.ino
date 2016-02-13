#define MODE3 "AT+CWMODE=3"
#define RESTART "AT+RST"
#define LIST_AP = "AT+CWLAP"
#define ENDL "\r\n"
#define MAX_RESTART 5
#define MAX_CONNECTION_TEMPTATIVE 5
#define NETWORK_NAME "\"ESP\""
#define NETWORK_PSWD "\"password\""
#define CREATE_NETWORK "AT+CWSAP="NETWORK_NAME","NETWORK_PSWD",3,4"
#define JOIN_NETWORK "AT+CWJAP="NETWORK_NAME","NETWORK_PSWD
#define QUIT_NETWORK "AT+CWQAP"

String ip="";
bool isHost = false;
bool isConnected = false;

void setup() {

    Serial.begin(9600);
    Serial1.begin(115200);

    Serial.println("Liste des define : ");
    Serial.println(NETWORK_NAME);
    Serial.println(NETWORK_PSWD);
    Serial.println(CREATE_NETWORK);
    Serial.println(JOIN_NETWORK);

    if(setupESP()==false){
      //A effacer si plus branché à l'ordi
      communicationWithESP();
    }
    setupNetwork();
    Serial.println("Setup finished");
}

bool endsWithOk(String str){
  return str.endsWith("OK"ENDL);
}

bool checkIfESPIsOk(){
  Serial1.println("AT");
  delay(500);
  int response = Serial1.available();
  while(Serial1.available()==true){
    Serial1.readString();
  }
  return response==11;
}

void restart(){
  Serial.println(RESTART);
  delay(1000);
  clearBuffer(false);
}

void quitAccessPoint(){
  Serial1.println(QUIT_NETWORK);
  delay(1000);
  while(Serial1.available()){
    Serial.print("ESP > ");
    Serial.println(Serial1.readString());
  }
}

bool setupESP(){
  int i;
  for(i = 0;i<MAX_RESTART;i++){
      restart();
      delay(1000);
      if (checkIfESPIsOk()==true){
          break;
      }
  }

  if (i==MAX_RESTART){
    Serial.println("Restart failed - ESP not ok");
    return false;
  }

  Serial1.println(MODE3);
}

bool contains(String src,String arg){
  int srcLen = src.length();
  int argLen = arg.length();

  for(int i = 0; i<srcLen; i++){
    int j=0;
    while(j<argLen){
      if(src[i+j]!=arg[j]){
        break;
      }
      j++;
      if (j+i>srcLen) return false;
    }
    if(j==argLen) return true;
  }
  return false;
}

void communicationWithESP(){
   Serial.println("Communication with ESP opened : ");
   while (Serial.available()==true) {
        String str = Serial.readString();
        if(contains(str,"EXIT")==true){
          return;
        }
        Serial1.println(str);
    }
    while (Serial1.available()==true) {
        Serial.write(Serial1.read());
    }
    Serial.println("Communication with ESP closed");
}

void setIp(){
  ip="Not implemented yet";
}

void clearBuffer(bool print){


  if( print){
    Serial.println("Clearing buffer : ");
    while(Serial1.available()==true){
      Serial.print("ESP > ");
      Serial.println(Serial1.readString());
    }
    Serial.println("Buffer cleared");
  }else{
    while(Serial1.available()==true){
      Serial1.readString();
    }
  }

  //rx_empty();
}

bool connectToNetwork(){
  clearBuffer(false);

  for(int i = 0; i<MAX_CONNECTION_TEMPTATIVE; i++){
    Serial1.println(JOIN_NETWORK);
    delay(5000);
    while(Serial1.available()==true){
      String response = Serial1.readString();
      if(contains(response,"OK")==true){
        return true;
      }
    }
    delay(1500);
    clearBuffer(false);
  }
  return false;
}

bool createNetwork(){
  for(int i = 0; i<MAX_CONNECTION_TEMPTATIVE; i++){
    Serial1.println(CREATE_NETWORK);
    delay(500);
    if(contains(Serial1.readString(),"OK")==true){
      return true;
    }
    delay(1000);
    //clearBuffer();
  }
  return false;
}


bool setupNetwork(){
  Serial.println("Connecting to network...");
  if(connectToNetwork()==true){
    Serial.println("Connection successfull !");
    setIp();
    isConnected = true;
    return true;
  }
  else{
    Serial.println("Connection failed");
    Serial.println("Creating network...");
    if(createNetwork()==true){
      Serial.println("Network created");
      setIp();
      isHost = true;
      return true;
    }
    else{
      Serial.println("Network creation failed");
    }
  }
  return false;
}

void loop() {


  if(isHost==true){
    Serial.println("I am the host : ");
  }
  if(isConnected==true){
    Serial.println("I am connected to the network");
  }

  Serial1.println("AT+CIFSR");
  Serial.println("IP :");
  Serial.println(Serial1.readString());

  delay(5000);
}
