#ifndef __ANCHOR_H__
#define __ANCHOR_H__
#include "ESP8266.h"
#include "Avt.h"

class Anchor {
    public:
        Anchor(uint8_t id);

        /****SET*****/
        void set_Position(float x, float y);
        void adjust_Range(float r);

        /****GET*****/
        uint8_t getId();
        float getX();
        float getY();
        float get_Range();



    private:
        uint8_t id;
        float x;
        float y;
        Avt *range;

};





class Mobile {
    public:
        Mobile(uint8_t id);

        /****SET*****/
        void adjust_X(float d);
        void adjust_Y(float d);


        /****GET*****/
        uint8_t getId();
        float getX();
        float getY();
        int getXDir(){return this->x->get_lastDir();};
        int getYDir(){return this->y->get_lastDir();};
        Vector<Anchor*> get_chosen_Anchor(){return chosen_Anchor;};

        Anchor* get_chosen_Anchor_I(int i){return chosen_Anchor[i];};
        void trilateration();
        void update_Anchor_Liste(Vector<Anchor*> liste);



    private:
        uint8_t id;
        Avt *x;
        Avt *y;
        Vector<Anchor*> all_Anchor_Liste;
        Vector<Anchor*> chosen_Anchor;


};
#endif
