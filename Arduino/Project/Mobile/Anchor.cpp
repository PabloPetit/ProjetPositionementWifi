#include "Anchor.h"

Anchor::Anchor(uint8_t id){
    this->id = id;
    this->range = new Avt();
}

void Anchor::set_Position(float x, float y){
    this->x = x;
    this->y = y;
}

void Anchor::adjust_Range(float r){
    this->range->update(r);
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
    return this->range->get_Value();
}


void Mobile::update_Anchor_Liste(Vector<Anchor*> liste){
    /* mise a jour de la liste des ancres
     *
     * Regarder si dans la liste des ancre choisie il y en a qui ne sont plus là
     * et les remplacer
     *
     */

     for(int i = 0; i< liste.size(); i++){
         this->all_Anchor_Liste.push_back(liste[i]);
         if(i < 3)this->chosen_Anchor.push_back(liste[i]);
     }

}








Mobile::Mobile(uint8_t id){
    this->id = id;
    this->x = new Avt();
    this->y = new Avt();
}

void Mobile::adjust_X(float d){
    this->x->update(d);
}
void Mobile::adjust_Y(float d){
    this->y->update(d);
}



uint8_t Mobile::getId(){
    return this->id;
}

float Mobile::getX(){
    return this->x->get_Value();
}

float Mobile::getY(){
    return this->y->get_Value();
}

// TODO : RE-WRITE
void Mobile::trilateration() {
    Anchor *anch1 = this->chosen_Anchor[0];
    Anchor *anch2 = this->chosen_Anchor[1];
    Anchor *anch3 = this->chosen_Anchor[2];

    float d = sqrt(pow(anch2->getX()-anch1->getX(), 2) + pow(anch2->getY()-anch1->getY(), 2)); // the distance between the centers P1 and P2 and

    Vector<float> ex; //  is the unit vector in the direction from P1 to P2.
    ex.push_back((anch2->getX()-anch1->getX())/d);
    ex.push_back((anch2->getY()-anch1->getY())/d);

    float i = ex[0]*(anch3->getX()-anch1->getX()) + ex[1]*(anch3->getY()-anch1->getY()); //  is the signed magnitude of the x component, in the figure 1 coordinate system, of the vector from P1 to P3

    Vector<float> ey; // is the unit vector in the y direction. Note that the points P1, P2, and P3 are all in the z = 0 plane of the figure 1 coordinate system.
    ey.push_back((anch3->getX()-anch1->getX()-i*ex[0])/
        sqrt(pow(anch3->getX()-anch1->getX()-i*ex[0],2) + pow(anch3->getY()-anch1->getY()-i*ex[1],2)));

    ey.push_back((anch3->getY()-anch1->getY()-i*ex[1])/
        sqrt(pow(anch3->getX()-anch1->getX()-i*ex[0],2) + pow(anch3->getY()-anch1->getY()-i*ex[1],2)));

    float j = ey[0] *(anch3->getX()-anch1->getX()) + ey[1]*(anch3->getY()-anch1->getY()); //is the signed magnitude of the y component, in the figure 1 coordinate system, of the vector from P1 to P3.


    float x = (pow(anch1->get_Range(),2) - pow(anch2->get_Range(),2) + pow(d,2))/ (2 * d);
    float y = (pow(anch1->get_Range(),2) - pow(anch3->get_Range(),2) + pow(i,2) + pow(j,2))/(2*j) - i*x/j;

    // gives the points in the original coordinate system since  e_x, e_y and e_z, the basis unit vectors, are expressed in the original coordinate system.
    this->adjust_X(anch1->getX()+ x*ex[0] + y*ey[0]);
    this->adjust_Y(anch1->getX()+ x*ex[1] + y*ey[1]);

}
