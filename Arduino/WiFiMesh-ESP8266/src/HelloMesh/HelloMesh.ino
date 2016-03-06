#include "ESP8266wifi.h"
#include "WiFiMesh.h"

WiFiMesh mesh_node;

/**
 * Callback for when other nodes send you data
 *
 * @request The string received from another node in the mesh
 * @returns The string to send back to the other node
 */
String manageRequest(String request)
{
	/* Print out received message */
	Serial.print("received: ");
	Serial.println(request);

	/* return a string to send back */
	return String("Hello world response.");
}

void setup()
{
  /* Create the mesh node object */
  mesh_node = WiFiMesh(ESP.getChipId(), manageRequest);

	Serial.begin(115200);
	delay(10);

	Serial.println();
	Serial.println();
	Serial.println("Setting up mesh node...");

	/* Initialise the mesh node */
	mesh_node.begin();
}

void loop()
{
	/* Accept any incoming connections */
	mesh_node.acceptRequest();

	/* Scan for other nodes and send them a message */
	mesh_node.attemptScan("Hello world request.");
	delay(1000);
}
