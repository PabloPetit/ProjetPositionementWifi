import random
import time
import math

class Avt:

    DELTA_MULTI = 1.5

    def __init__(self,mini,maxi,tolerance):
        self.mini = mini
        self.maxi = maxi
        self.currentVal = mini
        self.tolerance = tolerance
        self.delta = maxi
        self.it = 0
        self.sens = 0 # -1 0 ou 1
        self.itMSens = 0


    def update(self,val):

        error = self.currentVal - val
        self.it+=1

        if error > 0 :
            self.adjust(1)
            self.currentVal = max(self.mini, self.currentVal - self.delta)

        elif error < 0 :
            self.adjust(-1)
            self.currentVal = min(self.maxi, self.currentVal + self.delta)
        else :
            self.adjust(0)

    def adjust(self,sens):

        if sens == self.sens :
            self.itMSens += 1
            self.delta *= Avt.DELTA_MULTI
            if self.delta > self.maxi :
                self.delta = self.maxi

        else:
            self.itMSens -= 1
            self.delta /= Avt.DELTA_MULTI
            if self.delta < self.mini :
                self.delta = self.mini

        self.sens = sens


"""
avt = avt.py(0,10,0.0001)
v= []
ds = []
delta = []
i = 0

its = 400
sigma = 4

while i < its :

    dist = random.gauss(5,sigma)

    #print("Distance envoyee : "+str(dist))
    avt.update(dist)
    v.append(avt.currentVal)
    ds.append(dist)
    delta.append(avt.delta)
    #time.sleep(0.1)
    i+=1

plt.plot(ds)
plt.plot(v)

print(avt.currentVal)
#print(delta)
plt.plot(delta)
#plt.ylabel('some numbers')
plt.show()
"""