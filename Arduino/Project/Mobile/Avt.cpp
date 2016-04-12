#include "Avt.h"



void Avt::update(float value){
    if(!this->init){
        this->current_Val = value;
        this->init = true;
        return;
    }
    this->iteration++;
    float error = this->current_Val - value;

    if(error > 0){
        this->adjust(UP);
        this->current_Val = max(MIN, this->current_Val - this->delta);
        return;
    }
    if(error < 0){
        this->adjust(DOWN);
        this->current_Val = min(MAX, this->current_Val + this->delta);
        return;
    }

    this->adjust(EQUAL);
    return;
}

void Avt::adjust(int direction){
    if(direction == this->last_direction){
        this->delta *= DELTA_MULTI;
        this->delta = min(this->delta, MAX);
    }
    else {
        this->delta /= DELTA_MULTI;
        this->delta = max(this->delta, MIN);
    }
    this->last_direction = direction;
}

Avt::Avt(){
    this->current_Val = MIN;
    this->delta = 5;
    this->iteration = 0;
    this->last_direction = 0;
    // si premiere fois peut-être prendre directement la premiere val
    this->init = false;
}
