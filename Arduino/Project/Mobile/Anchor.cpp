#include "Anchor.h"

Anchor::Anchor(int id){
    this->id = id;
}

void Anchor::set_Position(int x, int y){
    this->x = x;
    this->y = y;
}

void Anchor::set_Range(float r){
    this->last_Range = r;
}

int Anchor::getId(){
    return this->id;
}

int Anchor::getX(){
    return this->x;
}

int Anchor::getY(){
    return this->y;
}

float Anchor::get_Range(){
    return this->last_Range;
}
