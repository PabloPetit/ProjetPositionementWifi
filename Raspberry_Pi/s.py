import random
import time
import matplotlib.pyplot as plt
import math





fichier = open("./Server/log100Rate.txt", "r")

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

#plt.plot(IT, R1, 'r-')#plt.plot(IT, R1, 'r-')







print(len(R3))
plt.plot(IT, R3, 'b-')
plt.plot(IT, avtR3, 'g-')
#plt.plot(X, Y, 'r--')
#plt.plot(X, Y, 'b.')
#plt.plot(R2)
plt.show()
