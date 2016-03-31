#include "Anchor.h"

Anchor::Anchor(uint8_t id){
    this->id = id;
}

void Anchor::set_Position(int x, int y){
    this->x = x;
    this->y = y;
}

void Anchor::set_Range(float r){
    this->last_Range = r;
}

uint8_t Anchor::getId(){
    return this->id;
}

float Anchor::getX(){
    return this->x;
}

float Anchor::getY(){
    return this->y;
}

float Anchor::get_Range(){
    return this->last_Range;
}
