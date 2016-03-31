#ifndef __ANCHOR_H__
#define __ANCHOR_H__
#include "ESP8266.h"

class Anchor {
    public:
        Anchor(uint8_t id);

        /****SET*****/
        void set_Position(int x, int y);
        void set_Range(float r);

        /****GET*****/
        uint8_t getId();
        float getX();
        float getY();
        float get_Range();



    private:
        uint8_t id;
        float x;
        float y;
        float last_Range;

};
#endif
