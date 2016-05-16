
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


def positionBrut(logs):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    #plt.suptitle(titre)
    xAvt = logs.X
    yAvt = logs.Y
    xBrut, yBrut = getXYBrut(logs)
    ''' '''

    t = np.arange(len(xAvt))
    ax.scatter(xBrut,yBrut,c=t, label="Brut")
    plt.ylabel('cm')
    plt.xlabel('cm')


    #ax.legend(loc='upper left')
    ax.grid()


    plt.show()
    pass

def positionAVT(logs):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    #plt.suptitle(titre)
    xAvt = logs.X
    yAvt = logs.Y
    ''' '''

    t = np.arange(len(xAvt))
    ax.scatter(xAvt,yAvt,c=t, label="Avt")
    plt.ylabel('cm')
    plt.xlabel('cm')


    #ax.legend(loc='upper left')
    ax.grid()


    plt.show()
    pass


def moy(tab):

    s = 0
    for e in tab:
        s += e
    return s/len(tab)

def getXYBrut(logs):
    xBrut = []
    yBrut = []

    for i in range(len(logs.R1)):
        xTmp,yTmp = trilaterate(logs.xC,logs.yC,logs.R1[i],logs.xB,logs.yB,logs.R2[i],logs.xA,logs.yA,logs.R3[i])
        xBrut.append(xTmp)
        yBrut.append(yTmp)
    '''for i in range(60, len(logs.R1)):
        #print( str(i) + " " + str(logs.R1[i]) + " " + str(logs.R2[i]) + " " +str(logs.R3[i]) + " " + str(x) + " " +str(y) )

        xTmp,yTmp = trilaterate(logs.xA,logs.yA,logs.R1[i],logs.xB,logs.yB,logs.R2[i],logs.xC,logs.yC,logs.R3[i])
        #print( str(i) + " " + str(logs.R1[i]) + " " + str(logs.R2[i]) + " " +str(logs.R3[i]) + " " + str(xTmp) + " " +str(yTmp) )
        xBrut.append(xTmp)
        yBrut.append(yTmp)
    '''
    return xBrut, yBrut

def getXYMoyenne(logs, cut=0):
    R11 = logs.R1[:cut]
    R12 = logs.R1[cut:]
    MR1 = [moy(R11[max(0, i-9): i]) for i in range(1, len(R11))]
    MR12 = [moy(R12[max(0, i-9): i]) for i in range(1, len(R12))]


    R21 = logs.R2[:cut]
    R22 = logs.R2[cut:]
    MR2 = [moy(R21[max(0, i-9): i]) for i in range(1, len(R21))]
    MR22 = [moy(R22[max(0, i-9): i]) for i in range(1, len(R22))]


    R31 = logs.R3[:cut]
    R32 = logs.R3[cut:]
    MR3 = [moy(R31[max(0, i-9): i]) for i in range(1, len(R31))]
    MR32 = [moy(R32[max(0, i-9): i]) for i in range(1, len(R32))]

    XX = []
    YY = []

    for i in range(len(MR1)):

        x, y = trilaterate(logs.xC, logs.yC, MR1[i], logs.xB, logs.yB, MR2[i],
            logs.xA,logs.yA, MR3[i])

        XX += [x]
        YY += [y]

    for i in range(len(MR12)):
        x, y = trilaterate(logs.xC, logs.yC, MR12[i], logs.xB, logs.yB, MR22[i],
            logs.xA,logs.yA, MR32[i])
        #print( str(i) + " " + str(MR12[i]) + " " + str(MR22[i]) + " " +str(MR32[i]) + " " + str(x) + " " +str(y) )
        XX += [x]
        YY += [y]

    return XX, YY


def positionMoyenne(logs, cut=0):
    fig = plt.figure()
    #plt.suptitle(titre)
    ax = fig.add_subplot(111)

    if cut is 0:
        cut = len(logs.X)
    xAvt = logs.X
    yAvt = logs.Y
    xMoy, yMoy = getXYMoyenne(logs, cut)

    t = np.arange(len(xMoy))
    ax.scatter(xMoy, yMoy, c=t, label="Moyenne")
    plt.ylabel('cm')
    plt.xlabel('cm')
    #ax.legend(loc='upper left')
    ax.grid()


    plt.show()
    pass


def distanceAVT(log):
    BrutR2 = logs.R2
    AvtR2 = logs.avtR2
    MoyenneR2 = [moy(BrutR2[max(0, i-9): i+1]) for i in range(0, len(BrutR2))]

    fig = plt.figure()

    ax = fig.add_subplot(111)
    #ax.suptitle(titre)
    ax.plot(logs.IT, MoyenneR2, 'r-')
    ax.plot(logs.IT, MoyenneR2, 'r+', label="Moyenne")
    ax.plot(logs.IT, BrutR2, 'b-')
    ax.plot(logs.IT, BrutR2, 'b+', label="Brut")
    ax.plot(logs.IT, AvtR2, 'g-')
    ax.plot(logs.IT, AvtR2, 'g+', label="Avt")
    #ax.legend(loc='upper right')
    ax.grid()
    plt.show()

    pass


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

titre = sys.argv[2]
logs = logs()
logs.readLogs(sys.argv[1])
positionBrut(logs)
positionMoyenne(logs)
positionAVT(logs)
#distanceAVT(logs)





"""
try :
    logs = logs()
    logs.readLogs(sys.argv[0])
    positionBrutPlusAVT(logs)
except :
    print(helpMess)
"""
