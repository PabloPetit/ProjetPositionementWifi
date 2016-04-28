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
        void trilateration();
        bool add_Anchor_Id(Anchor* a);
        bool remove_Anchor_Id(uint8_t id);
        Anchor* get_Anchor(int i){return this->all_Anchor_Liste[i];};
        void update_Anchor_Liste(Vector<Anchor*> liste);
        size_t get_anchor_size(){return this->all_Anchor_Liste.size();};



    private:
        uint8_t id;
        Avt *x;
        Avt *y;
        Vector<Anchor*> all_Anchor_Liste;


};
#endif
