import random
import time
import matplotlib.pyplot as plt
from math import *
import numpy as np


fichier = open("/media/data/git/P-Android_M1/Raspberry_Pi/Logs/Final/static100-50.txt", "r")

X = []
Y = []
R1 = []
R2 = []
R3 = []
IT = []

avtR1 = []
avtR2 = []
avtR3 = []
lines = fichier.readlines()
for l in lines:
    ll = l.split(" ")
    X += [float(ll[0])]
    Y += [float(ll[1])]
    avtR1 += [float(ll[2])]
    R1 += [float(ll[3])]
    avtR2 += [float(ll[4])]
    R2 += [float(ll[5])]
    avtR3 += [float(ll[6])]
    R3 += [float(ll[7])]
    IT += [float(ll[8])]


def trilaterate(xA,yA,dA,xB,yB,dB,xC,yC,dC):

    d = sqrt(pow(xB-xA,2)+pow(yB-yA,2))


    ex = [0]*2
    ex[0] = (xB - xA) / d
    ex[1] = (yB - yA) / d

    i = ex[0]*(xC - xA) + ex[1]*(yC - yA)

    ey = [0]*2

    ey[0] = (xC-xA-i*ex[0])/sqrt(pow(xC-xA-i*ex[0],2) + pow(yC-yA-i*ex[1],2))
    ey[1] = (yC-yA-i*ex[1])/sqrt(pow(xC-xA-i*ex[0],2) + pow(yC-yA-i*ex[1],2))

    j = ey[0] * (xC-xA) + ey[1]*(yC-yA)


    x = ( dA*dA - dB*dB + d*d ) / (2*d)
    y = (dA*dA - dC*dC + i*i + j*j)/(2*j) - i*x/j;


    resX = xA+ x*ex[0] + y*ey[0]
    resY = yA+ x*ex[1] + y*ey[1]

    return resX, resY





def moy(tab):

    s = 0
    for e in tab:
        s += e
    return s/len(tab)

R11 = R1[:60]
R12 = R1[60:]
MR1 = [moy(R11[max(0, i-9): i]) for i in range(1, len(R11))]
MR12 = [moy(R12[max(0, i-9): i]) for i in range(1, len(R12))]


R21 = R2[:60]
R22 = R2[60:]
MR2 = [moy(R21[max(0, i-9): i]) for i in range(1, len(R21))]
MR22 = [moy(R22[max(0, i-9): i]) for i in range(1, len(R22))]


R31 = R3[:60]
R32 = R3[60:]
MR3 = [moy(R31[max(0, i-9): i]) for i in range(1, len(R31))]
MR32 = [moy(R32[max(0, i-9): i]) for i in range(1, len(R32))]


print(MR1)
print(MR2)
print(MR3)

XX = []
YY = []

for i in range(len(MR1)):
    x, y = trilaterate(100, 0, MR2[i], 0, 100, MR1[i], 0, 0, MR3[i])
    XX += [x]
    YY += [y]

for i in range(len(MR12)):
    x, y = trilaterate(100, 0, MR22[i], 0, 100, MR12[i], 0, 50, MR32[i])
    XX += [x]
    YY += [y]

t = np.arange(len(X))

#plt.plot(IT, R3, 'b-')
#plt.plot(IT, avtR3, 'g-')
plt.plot(XX, YY, 'g.')
plt.plot(X, Y, 'r.')
#plt.scatter(X,Y,c=t)
#plt.plot(X, Y, 'b.')
#plt.plot(R2)
plt.show()
