import socket
import time
import select
from queue import Queue
from threading import *
from proto import *


id = -1
ty = -1

console_queue = Queue()

socket_th = None # Thread qui gère le server
console_th = None # Thread qui gère la console


def main():
