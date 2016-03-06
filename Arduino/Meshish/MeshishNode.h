#ifndef __MESHISH_H__
#define __MESHISH_H__

#define MESHISH_HTTP_PORT 80
#define MESHISH_PRIMARY_IP "192.168.4.1"
#define MESHISH_MAX_AP_SCAN 100

#define  WL_CONNECTION_LOST 3
#define  WL_DISCONNECTED 0
#define  WL_CONNECTED 2
#define  WL_CONNECT_FAILED 4
#define  WL_IDLE_STATUS 4

#include "lib_esp.h"

class MeshishNode {

public:

  struct AccessPoint {
    String ssid;       // AP’s ssid
    int rssi;      // AP’s bssid
    int channel;     //scan a specific channel
    int encrypt;
    String mac;
    unsigned int nodeType;
  };

  enum nodeType{
    NODE_NONE,
    NODE_PRIMARY,
    NODE_SECONDARY
  };

  MeshishNode();
  ~MeshishNode();

  void setup(String password, bool primary=false);
  void loop();
  void makePrimary(bool primary=true);
  void debug(HardwareSerial* serial);
  bool isPrimary();
  void split(String line, char sep);
  void set_ap(String line, AccessPoint *tmp);
  // bool isConnectedToPrimary();
  // bool enableDefaultRoutes(bool b=true);
  unsigned int getStatus();

protected:

  void _setSSID();
  void _scanAndConnect();
  bool _generateSSID();
  unsigned int _getNodeType(const AccessPoint& ap);

  byte _encrypt;
  bool _isPrimary;
  bool _debug;
  bool _connectingToAP; // true when STA is connecting to AP
  bool _creatingAP; // true when AP is being created
  unsigned int _numNetworks;
  uint32_t _chipId;
  String _ssid;
  String _ssidPrefix;
  String _password;

  //ESP8266WebServer _server;
  AccessPoint _apList[MESHISH_MAX_AP_SCAN];
  HardwareSerial* _serial;
  int _status;
};

#endif /* __MESHISH_H__ */
