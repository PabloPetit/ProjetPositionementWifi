#include "MeshishNode.h"



MeshishNode::MeshishNode():
  _isPrimary(false),
  _numNetworks(0),
  _ssidPrefix("EL_ESP"),
  _ssid(""),
  _chipId(0),
  _serial(NULL),
  _debug(true),
  _connectingToAP(false),
  _creatingAP(false),
  _status(0),
  _password(""){}



  /*_server(ESP8266WebServer(80)){

}*/

MeshishNode::~MeshishNode(){

}

void MeshishNode::setup(String password, bool primary){

  //WiFi.mode(WIFI_AP_STA);
  esp_set_wifi_mode_both();


  //WiFi.disconnect();
  quit_AP();
  delay(100);

  _isPrimary = primary;
  _password = password;
  //_chipId = ESP.getChipId(); // change
  _chipId = micros();



  bool ssidGenerated = _generateSSID();

  if (!ssidGenerated && _debug){
    _serial->println("MeshishNode::setup: _generateSSID() returned false.");
  }

  if (_isPrimary && ssidGenerated){
    if (_debug){
      _serial->println("MeshishNode::setup: Primary node creating SSID \"" + _ssid + "\"");
    }
    //WiFi.softAP(_ssid.c_str());
    esp_set_Access_Point_Parameters(_ssid.c_str(), _password, 3,4);
    _creatingAP = true;
  }
  else{
    _scanAndConnect();
  }

  /*_server.on("/", [this](){
     _server.send(200, "text/plain", "welcome!");
  });

  _server.onNotFound([this](){
    _server.send(200, "text/plain", "404 file not found");
  });

  _server.begin();*/
}

void MeshishNode::loop(){

  if (getStatus() == WL_CONNECTION_LOST){
    _serial->println("MeshishNode::loop: connection lost");
  }
  else if(getStatus() == WL_DISCONNECTED){
    _serial->println("MeshishNode::loop: disconnected");
  }

  if (_connectingToAP){
    unsigned int status = getStatus();
    if (_debug){
      _serial->print("MeshishNode::loop: status ");
      _serial->println(status);
    }

    // connection established
    if (status == WL_CONNECTED){
      _connectingToAP = false;

      if (_debug){
        _serial->print("MeshishNode::loop: connection to \"");
        //_serial->print(WiFi.SSID()); CHANGE
        _serial->println("\" established.");
        _serial->print("MeshishNode::loop: recieved IP Address ");
        //_serial->println(WiFi.localIP());

        _serial->println(esp_get_formated_local_IP());
      }

      // now create a secondary AP
      bool ssidGenerated = _generateSSID();
      if (ssidGenerated){
        // WiFi.softAPConfig(IPAddress(192, 168, 4, 10),
        //                   IPAddress(192, 168, 4, 10),
        //                   IPAddress(255, 255, 255, 0));
        //WiFi.softAP(_ssid.c_str());
        esp_set_Access_Point_Parameters(_ssid.c_str(), _password, 3,4);
        _status = 5;
        _creatingAP = true;
      }

    } // connection failed
    else if (status == WL_CONNECT_FAILED){
      _connectingToAP = false;

      if (_debug){
        _serial->print("MeshishNode::loop: connection to ");
        //_serial->print(WiFi.SSID()); CHANGE
        _serial->println(" failed.");
      }
    } // still connecting...
    else if (status == WL_IDLE_STATUS){
      if (_debug){
        _serial->println("MeshishNode::loop: connection idle...");
      }
    }
  }
  else{
    // not _connectingToAP
  }

  if (_creatingAP){
    unsigned int status = getStatus();
    // connection established
    if (status == WL_CONNECTED){
      _creatingAP = false;
      if (_debug){
        _serial->println("MeshishNode::loop: Access point created.");
        //WiFi.printDiag(*_serial); ????
      }
    }
    else if (status == WL_CONNECT_FAILED){
      _creatingAP = false;
      if (_debug)
      {
      _serial->println("MeshishNode::loop: Failed to create access point.");
      }
    }
    else if (status == WL_IDLE_STATUS){
      if (_debug)
      {
        _serial->println("MeshishNode::loop: access point creation idle...");
      }
    }
  }

  //_server.handleClient();
}

void MeshishNode::debug(HardwareSerial* serial){
  _debug = true;
  _serial = serial;
}

void MeshishNode::makePrimary(bool primary){
  if (_isPrimary != primary) {

    _isPrimary = primary;
    //WiFi.disconnect();
    quit_AP();

    if (_generateSSID() && _isPrimary){
      //WiFi.softAP(_ssid.c_str());
      if (_debug){
        _serial->println("MeshishNode::makePrimary: _generateSSID() returned true.");
      }

      bool ret = esp_set_Access_Point_Parameters(_ssid.c_str(), _password, 3,4);
      if(ret)_status = 1;
      else _status = 4;
      _creatingAP = true;
    }
    else if (_debug){
      _serial->println("MeshishNode::makePrimary: _generateSSID() returned false.");
    }

  }
}

bool MeshishNode::isPrimary(){
  return _isPrimary;
}

// bool MeshishNode::isConnectedToPrimary()
// {

// }

// bool MeshishNode::enableDefaultRoutes(bool enable)
// {

// }

unsigned int MeshishNode::getStatus(){
  //return WiFi.status();
  int status = _status;
  bool current = qCWJAP();
  if(!current){
    if (status != 0 && status != 1) {
      _status = 3;
    }
  }
  if (status == 1) {
    return 2;
  }
  return _status; // CHANGE
}


void MeshishNode::_scanAndConnect(){
  if (_debug){
    _serial->println("scan start...");
  }

  //_numNetworks = WiFi.scanNetworks(); // get number
  String liste = getAPList();
  split(liste, '\n');
  //_numNetworks = 1; // deg
  if (_debug){
    _serial->print(_numNetworks);
    _serial->println(" networks found in scan");
  }

  // the index of the node with the highest rssi
  int maxDBmPrimary = -1;

  for (int i = 0; i < _numNetworks; i++){
    /*_apList[i] = AccessPoint();
    _apList[i].ssid     = WiFi.SSID(i);
    _apList[i].rssi     = WiFi.RSSI(i);
    _apList[i].encrypt  = WiFi.encryptionType(i);
    _apList[i].nodeType = _getNodeType(_apList[i]);
    */
    if (_apList[i].nodeType == NODE_PRIMARY){
      if (maxDBmPrimary == -1){
        maxDBmPrimary = i;
      }
      else{
        if (_apList[i].rssi > _apList[maxDBmPrimary].rssi){
          maxDBmPrimary = i;
        }
      }
    }

    if (_debug){
      _serial->print(_apList[i].ssid);
      _serial->print("\t");
      _serial->print(_apList[i].rssi);
      _serial->print("dBm\t");
      _serial->print("Encryption: ");
      _serial->print(_apList[i].encrypt);
      _serial->print("\tnodeType: ");
      _serial->println(_apList[i].nodeType);
    }
  }

  if (maxDBmPrimary != -1){
    if (_debug){
      _serial->print("MeshishNode::_scanAndConnect: connecting to ");
      _serial->println(_apList[maxDBmPrimary].ssid.c_str());
    }

    //if (_password.equals("")) WiFi.begin(_apList[maxDBmPrimary].ssid.c_str());
    if (_password.equals("")){
      bool ret = esp_join_Access_Point(_apList[maxDBmPrimary].ssid.c_str(), "");
      if(ret)_status = 2;
      else _status = 4;
    }
    else{
      bool ret = esp_join_Access_Point(_apList[maxDBmPrimary].ssid.c_str(), _password.c_str());
      if(ret)_status = 2;
      else _status = 4;
    }
    //else WiFi.begin(_apList[maxDBmPrimary].ssid.c_str(), _password.c_str());

    _connectingToAP = true;
  }
  else {
    makePrimary(true);
  }
}

bool MeshishNode::_generateSSID(){
  if (_isPrimary){
    _ssid = String("\""+_ssidPrefix + "_1_" + String(MESHISH_PRIMARY_IP) + "_" + String(_chipId)+"\"");
    if (_debug){
      _serial->print("MeshishNode::_generateSSID: _isPrimary, ssid:");
      _serial->println(_ssid);
    }
    return true;
  }
  else{

    if (getStatus() == WL_CONNECTED){
      //IPAddress ip = WiFi.localIP();
      String ip = esp_get_formated_local_IP();
      _ssid = String("\""+_ssidPrefix + "_0_" + ip + "_" + String(_chipId)+"\"");
      if (_debug){
      _serial->print("MeshishNode::_generateSSID: !_isPrimary, ssid:");
      _serial->println(_ssid);
      }
      return true;
    }
    else{
      if (_debug){
      _serial->println("MeshishNode::_generateSSID: !_isPrimary but status != WL_CONNECTED");
      }
    }

  }

  return false;
}


unsigned int MeshishNode::_getNodeType(const AccessPoint& ap){
  int start = 1;
  String prefix = ap.ssid.substring(start, _ssidPrefix.length()+start);

  if (prefix.equals(_ssidPrefix)){
    if (ap.ssid.substring(_ssidPrefix.length()+start, _ssidPrefix.length()+start + 3).equals("_1_")){
      return NODE_PRIMARY;
    }
    else if (ap.ssid.substring(_ssidPrefix.length()+start, _ssidPrefix.length()+start + 3).equals("_0_")){
      return NODE_SECONDARY;
    }
  }

  return NODE_NONE;
}

void MeshishNode::split(String line, char sep){
  int i = 0;
  int startIndex = 0;
  int endIndex = 0;
  while ((endIndex = line.indexOf(sep, startIndex)) != -1 && i < MESHISH_MAX_AP_SCAN -1) {
    _apList[i] = AccessPoint();
    String s = line.substring(startIndex, endIndex);
    set_ap(s, &_apList[i]);
    _apList[i].nodeType = _getNodeType(_apList[i]);
    startIndex = endIndex+1;
    i++;

  }
  String s = line.substring(startIndex, line.length());
  set_ap(s, &_apList[i]);
  _numNetworks = i;
}

void MeshishNode::set_ap(String line, AccessPoint *tmp){
  // ENC
  int index = line.indexOf('(')+1;
  String  myString = line.substring(index, index+1);;
  int myStringLength = myString.length()+1;
  char myChar[myStringLength];
  myString.toCharArray(myChar,myStringLength);
  tmp->encrypt = atoi(myChar);

  //SSID
  int start = index+2;
  int end = line.indexOf(',', start);
  tmp->ssid = line.substring(start, end);

  // RSSI
  start = end+1;
  end = line.indexOf(',', start);
  myString = line.substring(start, end);
  myStringLength = myString.length()+1;
  char myChar2[myStringLength];
  myString.toCharArray(myChar2,myStringLength);
  tmp->rssi = atoi(myChar2);

  //MAC
  start = end+1;
  end = line.indexOf(',', start);
  tmp->mac = line.substring(start, end);

  //CHANNEL
  start = end+1;
  end = line.indexOf(',', start);
  myString = line.substring(start, end);
  myStringLength = myString.length()+1;
  char myChar23[myStringLength];
  myString.toCharArray(myChar23,myStringLength);
  tmp->channel = atoi(myChar23);
}
