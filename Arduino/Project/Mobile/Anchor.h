#ifndef __ANCHOR_H__
#define __ANCHOR_H__
#include "ESP8266.h"

class Anchor {
    public:
        Anchor(uint8_t id);

        /****SET*****/
        void set_Position(float x, float y);
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





class Mobile {
    public:
        Mobile(uint8_t id);

        /****SET*****/
        void set_Position(float x, float y);
        void adjust_X(float d);
        void adjust_Y(float d);
        void setX(float nX);
        void setY(float nY);
        void update_Anchor_Liste(Vector<Anchor> liste);

        /****GET*****/
        uint8_t getId();
        float getX();
        float getY();



    private:
        uint8_t id;
        float x;
        float y;
        Vector<Anchor> all_Anchor_Liste;
        Vector<Anchor> chosen_Anchor;


};
#endif
