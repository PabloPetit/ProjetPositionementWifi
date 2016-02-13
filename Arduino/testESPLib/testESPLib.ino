
#define SSID        "ESP2"
#define PASSWORD    "password"

bool isHost = false;

void setup(void){
    Serial.begin(9600);
    Serial1.begin(115200);

    restart();
    

    if (eAT()) {
        Serial.print("AT OK\r\n");
    } else {
        Serial.print("AT err\r\n");
    }
    
    if (setOprToStationSoftAP()) {
        Serial.print("set mode3 ok\r\n");
    } else {
        Serial.print("set mode3 err\r\n");
    }

    Serial.print("try to join ");
    Serial.println(SSID);
    if (sATCWJAP(SSID, PASSWORD)) {
        Serial.print("Join ");
        Serial.print(SSID);
        Serial.println(" Success");
        Serial.println("IP: ");       
        Serial.println(getLocalIP().c_str());
    } 
    else {
        Serial.print("Join ");
        Serial.print(SSID);
        Serial.println(" Fail");
        Serial.print("try to create ");
        Serial.print(SSID);
        Serial.println(" Network");
        if (sATCWSAP(SSID, PASSWORD, 3,4)) {
            Serial.print("Create ");
            Serial.print(SSID);
            Serial.println(" Network Success");
            isHost = true;
        } 
        else {
            Serial.print("Create ");
            Serial.print(SSID);
            Serial.println(" Network Fail");
        }
    }
    
    
}

void loop(void){
  delay(3000);
  if(isHost){
    Serial.println("list des IP connectees");
    Serial.println(getJoinedDeviceIP());
  }
}

bool restart(void)
{
    unsigned long start;
    if (eATRST()) {
        delay(2000);
        start = millis();
        while (millis() - start < 3000) {
            if (eAT()) {
                delay(1500); /* Waiting for stable */
                return true;
            }
            delay(100);
        }
    }
    return false;
}

bool eAT(void)
{
    rx_empty();
    Serial1.println("AT");
    return recvFind("OK",1000);
}

void rx_empty(void) 
{
    while(Serial1.available() > 0) {
        Serial1.read();
    }
}

bool eATRST(void) 
{
    rx_empty();
    Serial1.println("AT+RST");
    return recvFind("OK", 1000);
}

bool recvFind(String target, uint32_t timeout)
{
    String data_tmp;
    data_tmp = recvString(target, timeout);
    if (data_tmp.indexOf(target) != -1) {
        return true;
    }
    return false;
}

String recvString(String target, uint32_t timeout)
{
    String data;
    char a;
    unsigned long start = millis();
    while (millis() - start < timeout) {
        while(Serial1.available() > 0) {
            a = Serial1.read();
      if(a == '\0') continue;
            data += a;
        }
        if (data.indexOf(target) != -1) {
            break;
        }   
    }
    return data;
}


bool setOprToStationSoftAP(void)
{
    uint8_t mode;
    if (!qATCWMODE(&mode)) {
        return false;
    }
    if (mode == 3) {
        return true;
    } else {
        if (sATCWMODE(3) && restart()) {
            return true;
        } else {
            return false;
        }
    }
}


bool qATCWMODE(uint8_t *mode) 
{
    String str_mode;
    bool ret;
    if (!mode) {
        return false;
    }
    rx_empty();
    Serial1.println("AT+CWMODE?");
    ret = recvFindAndFilter("OK", "+CWMODE:", "\r\n\r\nOK", str_mode, 1000); 
    if (ret) {
        *mode = (uint8_t)str_mode.toInt();
        return true;
    } else {
        return false;
    }
}


bool recvFindAndFilter(String target, String begin, String end, String &data, uint32_t timeout)
{
    String data_tmp;
    data_tmp = recvString(target, timeout);
    if (data_tmp.indexOf(target) != -1) {
        int32_t index1 = data_tmp.indexOf(begin);
        int32_t index2 = data_tmp.indexOf(end);
        if (index1 != -1 && index2 != -1) {
            index1 += begin.length();
            data = data_tmp.substring(index1, index2);
            return true;
        }
    }
    data = "";
    return false;
}

bool sATCWMODE(uint8_t mode)
{
    String data, data2;
    rx_empty();
    Serial1.print("AT+CWMODE=");
    Serial1.println(mode);
    
    data = recvString("OK", 1000);
    data2 = recvString("no change", 1000);
    if (data.indexOf("OK") != -1 || data2.indexOf("no change") != -1) {
        return true;
    }
    return false;
}


bool sATCWJAP(String ssid, String pwd)
{
    String data, data2;
    rx_empty();
    Serial1.print("AT+CWJAP=\"");
    Serial1.print(ssid);
    Serial1.print("\",\"");
    Serial1.print(pwd);
    Serial1.println("\"");
    
    data = recvString("OK", 10000);
    data2 = recvString("FAIL", 10000);
    if (data.indexOf("OK") != -1) {
        return true;
    }
    else if(data2.indexOf("FAIL") != -1){
      return false;
    }
    return false;
}


String getLocalIP(void)
{
    String list;
    eATCIFSR(list);
    return list;
}

bool eATCIFSR(String &list)
{
    rx_empty();
    Serial1.println("AT+CIFSR");
    return recvFindAndFilter("OK", "\r\r\n", "\r\n\r\nOK", list, 10000);
}

String getJoinedDeviceIP(void)
{
    String list;
    eATCWLIF(list);
    return list;
}

bool eATCWLIF(String &list)
{
    String data;
    rx_empty();
    Serial1.println("AT+CWLIF");
    return recvFindAndFilter("OK", "\r\r\n", "\r\n\r\nOK", list, 10000);
}


bool sATCWSAP(String ssid, String pwd, uint8_t chl, uint8_t ecn)
{
    String data, data2;
    rx_empty();
    Serial1.print("AT+CWSAP=\"");
    Serial1.print(ssid);
    Serial1.print("\",\"");
    Serial1.print(pwd);
    Serial1.print("\",");
    Serial1.print(chl);
    Serial1.print(",");
    Serial1.println(ecn);
    
    data = recvString("OK", 5000);
    data2 = recvString("ERROR", 5000);
    if (data.indexOf("OK") != -1) {
        return true;
    }
    return false;
}
