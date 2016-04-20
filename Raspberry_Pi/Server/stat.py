import random
import time
import matplotlib.pyplot as plt
import math





fichier = open("./log", "r")

X = []
Y = []
R1 = []
R2 = []
R3 = []
IT = []
lines = fichier.readlines()
for l in lines:
    ll = l.split(" ")
    X += [float(ll[0])]
    Y += [float(ll[1])]
    R1 += [float(ll[2])]
    R2 += [float(ll[3])]
    R3 += [float(ll[4])]
    IT += [float(ll[5])]

plt.plot(IT, X, 'r-')
#plt.plot(R2)
plt.show()
