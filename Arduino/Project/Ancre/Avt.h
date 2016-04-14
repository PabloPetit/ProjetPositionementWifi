#ifndef __AVT_H__
#define __AVT_H__

#include "Vector.h"

#define MIN 0
#define MAX 200
#define TOLERENCE 0.0001
#define DELTA_MULTI 1.2

#define UP 1
#define DOWN -1
#define EQUAL 0


class Avt {
    public:
        Avt();
        void update(float value);
        float get_Value(){return current_Val;};
        void adjust(int direction);

    private:
        boolean init;
        float current_Val;
        int iteration;
        float delta;
        int last_direction;


};


#endif
