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
        float getX();
        float getY();
        float get_Range();



    private:
        int id;
        float x;
        float y;
        float last_Range;

};
#endif
