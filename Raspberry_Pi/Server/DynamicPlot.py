import random

import matplotlib.pyplot as plt
import time





class DynamicPlot:

    def __init__(self,min_x, max_x):
        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.legend()
        self.line1, = self.ax.plot([], [] ,'-k',label='black')
        self.line2, = self.ax.plot([], [],'-r',label='red')
        self.A = []
        self.B = []

    def update(self,x,y):
        self.A.append(x)
        self.B.append(y)
        self.line1.set_ydata(self.A)
        self.line1.set_xdata(range(len(self.A)))
        self.line2.set_ydata(self.B)
        self.line2.set_xdata(range(len(self.B)))
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.draw()



