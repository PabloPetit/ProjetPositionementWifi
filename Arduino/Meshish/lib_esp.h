#ifndef __LIB_ESP__
#define __LIB_ESP__

#include <Arduino.h>
#define TIMEOUT 10000
#define ESP8266 Serial1


bool eps_restart(void);

bool eps_AT(void);

void rx_empty(void);

bool recvFind(String target);

String recvString(String target);

String recvString2(String target, String target2);

bool esp_set_wifi_mode_both(void);

bool esp_ask_wifi_mode(uint8_t *mode);

bool esp_set_wifi_mode(uint8_t mode);

bool recvFindAndFilter(String target, String begin, String end, String &data);

bool esp_join_Access_Point(String ssid, String pwd);

String esp_get_local_IP(void);

String esp_get_Joined_Device_IP(void);

bool esp_set_Access_Point_Parameters(String ssid, String pwd, uint8_t chl, uint8_t ecn);

bool quit_AP(void);

String getAPList(void);

String getIPStatus(void);

int getIPStatusInt(void);

bool qCWJAP();

String esp_get_formated_local_IP();

/**
     * Enable IP MUX(multiple connection mode).
     *
     * In multiple connection mode, a couple of TCP and UDP communication can be builded.
     * They can be distinguished by the identifier of TCP or UDP named mux_id.
     *
     * @retval true - success.
     * @retval false - failure.
     */
    bool enableMUX(void);

    /**
     * Disable IP MUX(single connection mode).
     *
     * In single connection mode, only one TCP or UDP communication can be builded.
     *
     * @retval true - success.
     * @retval false - failure.
     */
    bool disableMUX(void);


    /**
     * Create TCP connection in single mode.
     *
     * @param addr - the IP or domain name of the target host.
     * @param port - the port number of the target host.
     * @retval true - success.
     * @retval false - failure.
     */
    bool createTCP(String addr, uint32_t port);

    /**
     * Release TCP connection in single mode.
     *
     * @retval true - success.
     * @retval false - failure.
     */
    bool releaseTCP(void);

    /**
     * Register UDP port number in single mode.
     *
     * @param addr - the IP or domain name of the target host.
     * @param port - the port number of the target host.
     * @retval true - success.
     * @retval false - failure.
     */
    bool registerUDP(String addr, uint32_t port);

    /**
     * Unregister UDP port number in single mode.
     *
     * @retval true - success.
     * @retval false - failure.
     */
    bool unregisterUDP(void);

    /**
     * Create TCP connection in multiple mode.
     *
     * @param mux_id - the identifier of this TCP(available value: 0 - 4).
     * @param addr - the IP or domain name of the target host.
     * @param port - the port number of the target host.
     * @retval true - success.
     * @retval false - failure.
     */
    bool createTCP(uint8_t mux_id, String addr, uint32_t port);

    /**
     * Release TCP connection in multiple mode.
     *
     * @param mux_id - the identifier of this TCP(available value: 0 - 4).
     * @retval true - success.
     * @retval false - failure.
     */
    bool releaseTCP(uint8_t mux_id);

    /**
     * Register UDP port number in multiple mode.
     *
     * @param mux_id - the identifier of this TCP(available value: 0 - 4).
     * @param addr - the IP or domain name of the target host.
     * @param port - the port number of the target host.
     * @retval true - success.
     * @retval false - failure.
     */
    bool registerUDP(uint8_t mux_id, String addr, uint32_t port);

    /**
     * Unregister UDP port number in multiple mode.
     *
     * @param mux_id - the identifier of this TCP(available value: 0 - 4).
     * @retval true - success.
     * @retval false - failure.
     */
    bool unregisterUDP(uint8_t mux_id);


    /**
     * Set the timeout of TCP Server.
     *
     * @param timeout - the duration for timeout by second(0 ~ 28800, default:180).
     * @retval true - success.
     * @retval false - failure.
     */
    bool setTCPServerTimeout(uint32_t timeout = 180);

    /**
     * Start TCP Server(Only in multiple mode).
     *
     * After started, user should call method: getIPStatus to know the status of TCP connections.
     * The methods of receiving data can be called for user's any purpose. After communication,
     * release the TCP connection is needed by calling method: releaseTCP with mux_id.
     *
     * @param port - the port number to listen(default: 333).
     * @retval true - success.
     * @retval false - failure.
     *
     * @see String getIPStatus(void);
     * @see uint32_t recv(uint8_t *coming_mux_id, uint8_t *buffer, uint32_t len, uint32_t timeout);
     * @see bool releaseTCP(uint8_t mux_id);
     */
    bool startTCPServer(uint32_t port = 333);

    /**
     * Stop TCP Server(Only in multiple mode).
     *
     * @retval true - success.
     * @retval false - failure.
     */
    bool stopTCPServer(void);

    /**
     * Start Server(Only in multiple mode).
     *
     * @param port - the port number to listen(default: 333).
     * @retval true - success.
     * @retval false - failure.
     *
     * @see String getIPStatus(void);
     * @see uint32_t recv(uint8_t *coming_mux_id, uint8_t *buffer, uint32_t len, uint32_t timeout);
     */
    bool startServer(uint32_t port = 333);

    /**
     * Stop Server(Only in multiple mode).
     *
     * @retval true - success.
     * @retval false - failure.
     */
    bool stopServer(void);

    /**
     * Send data based on TCP or UDP builded already in single mode.
     *
     * @param buffer - the buffer of data to send.
     * @param len - the length of data to send.
     * @retval true - success.
     * @retval false - failure.
     */
    bool send(const uint8_t *buffer, uint32_t len);

    /**
     * Send data based on one of TCP or UDP builded already in multiple mode.
     *
     * @param mux_id - the identifier of this TCP(available value: 0 - 4).
     * @param buffer - the buffer of data to send.
     * @param len - the length of data to send.
     * @retval true - success.
     * @retval false - failure.
     */
    bool send(uint8_t mux_id, const uint8_t *buffer, uint32_t len);

    /**
     * Receive data from TCP or UDP builded already in single mode.
     *
     * @param buffer - the buffer for storing data.
     * @param buffer_size - the length of the buffer.
     * @param timeout - the time waiting data.
     * @return the length of data received actually.
     */
    uint32_t recv(uint8_t *buffer, uint32_t buffer_size, uint32_t timeout = 1000);

    /**
     * Receive data from one of TCP or UDP builded already in multiple mode.
     *
     * @param mux_id - the identifier of this TCP(available value: 0 - 4).
     * @param buffer - the buffer for storing data.
     * @param buffer_size - the length of the buffer.
     * @param timeout - the time waiting data.
     * @return the length of data received actually.
     */
    uint32_t recv(uint8_t mux_id, uint8_t *buffer, uint32_t buffer_size, uint32_t timeout = 1000);

    /**
     * Receive data from all of TCP or UDP builded already in multiple mode.
     *
     * After return, coming_mux_id store the id of TCP or UDP from which data coming.
     * User should read the value of coming_mux_id and decide what next to do.
     *
     * @param coming_mux_id - the identifier of TCP or UDP.
     * @param buffer - the buffer for storing data.
     * @param buffer_size - the length of the buffer.
     * @param timeout - the time waiting data.
     * @return the length of data received actually.
     */
    uint32_t recv(uint8_t *coming_mux_id, uint8_t *buffer, uint32_t buffer_size, uint32_t timeout = 1000);


    /*
     * Receive a package from uart.
     *
     * @param buffer - the buffer storing data.
     * @param buffer_size - guess what!
     * @param data_len - the length of data actually received(maybe more than buffer_size, the remained data will be abandoned).
     * @param timeout - the duration waitting data comming.
     * @param coming_mux_id - in single connection mode, should be NULL and not NULL in multiple.
     */
    uint32_t recvPkg(uint8_t *buffer, uint32_t buffer_size, uint32_t *data_len, uint32_t timeout, uint8_t *coming_mux_id);


    bool eAT(void);
    bool eATRST(void);
    bool eATGMR(String &version);

    bool qATCWMODE(uint8_t *mode);
    bool sATCWMODE(uint8_t mode);
    bool sATCWJAP(String ssid, String pwd);
    bool eATCWLAP(String &list);
    bool eATCWQAP(void);
    bool sATCWSAP(String ssid, String pwd, uint8_t chl, uint8_t ecn);
    bool eATCWLIF(String &list);

    bool eATCIPSTATUS(String &list);
    bool sATCIPSTARTSingle(String type, String addr, uint32_t port);
    bool sATCIPSTARTMultiple(uint8_t mux_id, String type, String addr, uint32_t port);
    bool sATCIPSENDSingle(const uint8_t *buffer, uint32_t len);
    bool sATCIPSENDMultiple(uint8_t mux_id, const uint8_t *buffer, uint32_t len);
    bool sATCIPCLOSEMulitple(uint8_t mux_id);
    bool eATCIPCLOSESingle(void);
    bool eATCIFSR(String &list);
    bool sATCIPMUX(uint8_t mode);
    bool sATCIPSERVER(uint8_t mode, uint32_t port = 333);
    bool sATCIPSTO(uint32_t timeout);

#endif /* #ifndef __LIB_ESP__ */
