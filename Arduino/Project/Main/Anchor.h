#ifndef __ANCHOR_H__
#define __ANCHOR_H__


class Anchor {
    public:
        Anchor(int id);

        /****SET*****/
        void set_Position(int x, int y);
        void set_Range(float r);

        /****GET*****/
        int getId();
        int getX();
        int getY();
        float get_Range();



    private:
        int id;
        int x;
        int y;
        float last_Range;


#endif
