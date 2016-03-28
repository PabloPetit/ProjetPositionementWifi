import socket
import time
import select
from queue import Queue
from threading import *
from proto import *
import sys
import random


id = -1
ty = -1
pos = (-1,-1,-1)

console_queue = Queue()

socket_th = None # Thread qui gère les communications
console_th = None # Thread qui gère la console


def main():
     console_th = console()
     socket_th = com("localhost",4010)

     console_th.start()
     socket_th.start()

class console(Thread):

    global TYPES
    TIMEOUT = 5

    def __init__(self):
        Thread.__init__(self)
        self.queue = console_queue
        self.terminated = False

    def queueService(self):
        while not self.queue.empty():
            print(self.queue._get())

    def run(self):
        while(True):
            if self.terminated :
                return
            self.queueService()
            i, o, e = select.select( [sys.stdin], [], [], console.TIMEOUT )
            if i :
                st = sys.stdin.readline().strip()

                if st.lower() in ["exit","quit"]:
                    self.quit()

    def quit(self, empty = True):
        self.terminated = True
        print("La console a été coupée")
        if empty :
            print("Vidage de la file :")
            self.queueService()


class com(Thread):

    MAX_ATTEMPS = 5 #Nombre de repetition pour les communication
    TIMEOUT = 5 #Temps d'attente d'une reponse

    def __init__(self,host,port):
        Thread.__init__(self)
        self.host = host
        self.port = port
        self.sock = None

    def ask_id(self):
        global TYPES
        i = 0
        while i < com.MAX_ATTEMPS :
            try:
                select.select([self.sock],[], [], com.TIMEOUT)
            except select.error:
                pass
            else:
                msg = message(string=self.sock.recv(TYPES['BYTE_SZ']))
                if msg.ty == TYPES['SET_ID'] :
                    id = int(msg.msg)
                    self.sock.send(message(dest=0,ty=TYPES['CNF_ID']).str())
                    return True
        return False

    def set_id(self):
        global TYPES
        """
            On considere pour l'instant que l'ancre ou le mobile ne
            fait rien s'il n'as pas d'id
        """
        while True :
            if not self.ask_id():
                self.sock.send(message(dest=0,ty=TYPES['ASK_ID']).str())
            else :
                return

    def inform_type(self,dest):
        if ty == TYPES['TY_ANCH'] :
            self.sock.send(message(dest=dest,ty=TYPES['TY_ANCH']).str())
        elif ty == TYPES['TY_MOB'] :
            self.sock.send(message(dest=dest,ty=TYPES['TY_MOB']).str())
        elif ty == TYPES['TY_BOTH'] :
            self.sock.send(message(dest=dest,ty=TYPES['TY_BOTH']).str())

    def send_dist(self,dest):
        dist = random.uniform(3, 7)
        self.sock.send(message(dest=dest,ty=TYPES['RES_DT'],message = str(dist)).str())

    def send_pos(self,dest):
        global pos
        pos = str(pos(0))+"-"+str(pos(1))+"-"+str(pos(2))
        self.sock.send(message(dest=dest,ty=TYPES['RES_PS'],message = str(pos)).str())

    def run(self):
        global id

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        self.set_id()

        console_queue.put("L'id a été reçu : "+str(id))

        self.loop()

    def loop(self):
         global TYPES
         msg = message(string=self.client.sock.recv(TYPES['BYTE_SZ']).decode())

         if msg.ty == TYPES['ASK_TY']:
             self.inform_type(msg.dest)

         elif msg.ty == TYPES['ASK_DT']:
             self.send_dist(int(msg.msg))

         elif msg.ty == TYPES['ASK_PS']:
            self.send_pos(int(msg.msg))



main()
