#include "Anchor.h"

Anchor::Anchor(uint8_t id){
    this->id = id;
}

void Anchor::set_Position(float x, float y){
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


void update_Anchor_Liste(Vector<Anchor> liste){
    /* mise a jour de la liste des ancres
     *
     * Regarder si dans la liste des ancre choisie il y en a qui ne sont plus là
     * et les remplacer
     *
     */
}








Mobile::Mobile(uint8_t id){
    this->id = id;
}

void Mobile::set_Position(float x, float y){
    this->x = x;
    this->y = y;
}
void Mobile::setX(float nX){
    this->x = nX;
}
void Mobile::setY(float nY){
    this->y = nY;
}



uint8_t Mobile::getId(){
    return this->id;
}

float Mobile::getX(){
    return this->x;
}

float Mobile::getY(){
    return this->y;
}
