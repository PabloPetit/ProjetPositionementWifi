#include "MeshishNode.h"

MeshishNode node;

void setup() {

  Serial.begin(9600);
  ESP8266.begin(115200);
  node.debug(&Serial);
  node.setup("\"123456789\"", false);
}

void loop() {
  // put your main code here, to run repeatedly:
  node.loop();
  //Serial.println(node.getStatus());
}
