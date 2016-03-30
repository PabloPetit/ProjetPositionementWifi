import socket
import time
import select
from queue import Queue
from threading import *
from proto import *
import sys
import random


id = -1
ty = 1
pos = (random.randint(50, 100),random.randint(50, 100),random.randint(50, 100))

console_queue = Queue()

socket_th = None # Thread qui gère les communications
console_th = None # Thread qui gère la console

#TODO : try catch autour des send et recv

def main():
     console_th = console()
     socket_th = com("localhost",4002)

     console_th.start()
     socket_th.start()

class console(Thread):

    global TYPES
    TIMEOUT = 1

    def __init__(self):
        Thread.__init__(self)
        self.queue = console_queue
        self.terminated = False

    def queueService(self):
        while not self.queue.empty():
            tmp = self.queue._get()
            if tmp.lower() in ["quit","exit"]:
                self.quit()
                return
            print(tmp)

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
        self.terminated = False

    def ask_id(self):
        global TYPES
        global id
        i = 0
        while i < com.MAX_ATTEMPS :
            try:
                console_queue.put("En attente de récéption de l'id ["+str(i+1)+"]")
                select.select([self.sock],[], [], com.TIMEOUT)
            except select.error:
                pass
            else:
                msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))

                if msg.ty == TYPES['SET_ID'] :
                    id = int(msg.msg[0])
                    self.sock.send(message(dest=0,ty=TYPES['CNF_ID']).str())
                    return True
                else :
                    console_queue.put("Message reçu non conforme : \n"+msg.toString())
            i+=1
        return False

    def set_id(self):
        global TYPES
        global id
        """
            On considere pour l'instant que l'ancre ou le mobile ne
            fait rien s'il n'as pas d'id
        """

        console_queue.put("Récuperation de l'id ...")

        while True :
            if not self.ask_id():
                console_queue.put("La récuperation de l'id a échoué.")
                console_queue.put("Envoi d'une nouvelle demande")
                try :
                    self.sock.send(message(dest=0,ty=TYPES['ASK_ID']).str())
                except socket.error:
                    console_queue.put("Envoi impossible")
                    #TODO: faire un truc
                    pass
            else :
                console_queue.put("L'id a bien été récupéré : ID = "+str(id))
                return

    def inform_type(self,dest):
        if ty == TYPES['TY_ANCH'] :
            self.sock.send(message(dest=dest,ty=TYPES['RES_TY'], msg=TYPES['TY_ANCH']).str())
        elif ty == TYPES['TY_MOB'] :
            self.sock.send(message(dest=dest,ty=TYPES['RES_TY'], msg=TYPES['TY_MOB']).str())
        elif ty == TYPES['TY_BOTH'] :
            self.sock.send(message(dest=dest,ty=TYPES['RES_TY'], msg=TYPES['TY_BOTH']).str())

    def send_dist(self,dest):
        dist = random.uniform(3, 7)
        self.sock.send(message(dest=dest,ty=TYPES['RES_DT'],message = str(dist)).str())

    def send_pos(self,dest):
        global pos
        pos = str(pos(0))+"-"+str(pos(1))+"-"+str(pos(2))
        self.sock.send(message(dest=dest,ty=TYPES['RES_PS'],message = str(pos)).str())

    def connexion(self):
        console_queue.put("Lancement du server...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            #self.sock.setblocking(1)
        except socket.error:
            console_queue.put("Connexion impossible")
            console_queue.put("quit")
            self.terminated = True
            return False
        console_queue.put("Connexion réussie")
        return True

    def run(self):
        global id

        if not self.connexion() :
            return

        self.set_id()

        self.loop()

    def loop(self):
         global TYPES

         while True :
             if self.terminated :
                 return

             #msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
             bytes = bytearray()

             #size = self.sock.recv_into(bytes)
             msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
             console_queue.put("Un message a été reçu : ")

             #console_queue.put(str(msg.bytes))

             #if size == TYPES['BYTE_SZ'] :
             #msg = message(bytes=bytes)

             if msg.ty == TYPES['ASK_TY']:
                console_queue.put("Demande de type reçu du client "+str(int(msg.msg[0])))
                self.inform_type(int(msg.msg[0]))

             elif msg.ty == TYPES['ASK_DT']:
                console_queue.put("Demande d'évaluation de distance reçu du client "+str(int(msg.msg[0])))
                self.send_dist(int(msg.msg[0]))

             elif msg.ty == TYPES['ASK_PS']:
                console_queue.put("Demande de position reçu du client "+str(int(msg.msg[0])))
                self.send_pos(int(msg.msg[0]))

             elif msg.ty == TYPES['CNF_TY']:
                 console_queue.put("Le serveur confirme qu'il as bien reçu le type")

             else :
                console_queue.put("Message incompris : "+msg.toString())
             time.sleep(1)

main()
