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