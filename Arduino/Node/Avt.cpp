#include "Avt.h"



void Avt::update(float value){
    if(!this->init){
        this->current_Val = value;
        this->init = true;
        return;
    }
    this->iteration++;
    float error = this->current_Val - value;

    if(error > TOLERENCE){
        this->adjust(UP);
        this->current_Val = max(MIN, this->current_Val - this->delta);
        return;
    }
    if(error < -TOLERENCE){
        this->adjust(DOWN);
        this->current_Val = min(MAX, this->current_Val + this->delta);
        return;
    }

    this->adjust(EQUAL);
    return;
}

void Avt::adjust(int direction){
    if(direction == this->last_direction && direction != EQUAL){
        this->delta *= DELTA_MULTI;
        this->delta = min(this->delta, MAX_DELTA);
    }
    else {
        this->delta /= DELTA_DIV;
        this->delta = max(this->delta, MIN_DELTA);
    }
    this->last_direction = direction;
}

int Avt::get_lastDir(){
    return this->last_direction;
}

Avt::Avt(){
    this->current_Val = MIN;
    this->delta = 1;
    this->iteration = 0;
    this->last_direction = 0;
    // si premiere fois peut-être prendre directement la premiere val
    this->init = false;
}
