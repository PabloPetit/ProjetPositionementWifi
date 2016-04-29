
import random
import time
import matplotlib.pyplot as plt
from math import *
import sys

import numpy as np


class logs:

    def __init__(self):
        self.X = []
        self.Y = []
        self.R1 = []
        self.R2 = []
        self.R3 = []
        self.IT = []
        self.avtR1 = []
        self.avtR2 = []
        self.avtR3 = []
        self.xA = 0
        self.yA = 0
        self.xB = 100
        self.yB = 0
        self.xC = 0
        self.yC = 100


        self.xD = 0
        self.yD = 50


    def readLogs(self,path) :
        fichier = open(path, "r")
        lines = fichier.readlines()
        for l in lines:
            ll = l.split(" ")
            self.X += [float(ll[0])]
            self.Y += [float(ll[1])]
            self.avtR1 += [float(ll[2])]
            self.R1 += [float(ll[3])]
            self.avtR2 += [float(ll[4])]
            self.R2 += [float(ll[5])]
            self.avtR3 += [float(ll[6])]
            self.R3 += [float(ll[7])]
            self.IT += [float(ll[8])]


def positionBrutPlusAVT(logs):

    f, ax = plt.subplots()

    xAvt = logs.X
    yAvt = logs.Y

    xBrut, yBrut = getXYBrut(logs)

    ax.plot(xAvt,yAvt,'g.')
    ax.plot(xBrut,yBrut,'r.')

    pass

def getXYBrut(logs):
    xBrut = []
    yBrut = []

    for i in range(len(logs.R1)):
        xTmp,yTmp = trilaterate(logs.xA,logs.yA,logs.R1[i],logs.xB,logs.yB,logs.R2[i],logs.xC,logs.yC,logs.R3[i])
        xBrut.append(xTmp)
        yBrut.append(yTmp)

    return xBrut, yBrut


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


helpMess = "Not implemented yet"


logs = logs()
logs.readLogs(sys.argv[1])
positionBrutPlusAVT(logs)

plt.show()




"""
try :
    logs = logs()
    logs.readLogs(sys.argv[0])
    positionBrutPlusAVT(logs)
except :
    print(helpMess)
"""

