import random
import time
import matplotlib.pyplot as plt
from math import *
import sys

import numpy as np


f = open("./it_seconde.txt",'r')
l = [i for i in f.readlines()]
n = [int(n) for n in l]

f, ax = plt.subplots()


ax.plot(n,'g')

plt.show()