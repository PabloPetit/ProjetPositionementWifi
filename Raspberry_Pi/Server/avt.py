class Avt:

    def __init__(self,mini,maxi,toleranceMin,toleranceMax):
        self.mini = mini
        self.maxi = maxi
        self.currentVal = mini
        self.toleranceMin = toleranceMin
        self.toleranceMax = toleranceMax
        self.delta = toleranceMax
        self.it = 0
        self.sens = 0 # -1 0 ou 1


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
            self.delta *= 2
            if self.delta > self.toleranceMax :
                self.delta = self.toleranceMax

        else:
            self.delta *= 1/3.0
            if self.delta < self.toleranceMin :
                self.delta = self.toleranceMin

        self.sens = sens


