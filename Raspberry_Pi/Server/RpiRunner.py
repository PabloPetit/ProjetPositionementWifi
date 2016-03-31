import socket
import select
import sys
import time
import random
from queue import Queue
from threading import *
from proto import *


class RpiRunner(Thread):

    TIMEOUT = 5
    MAX_ATTEMPS = 5

    def __init__(self,ty,host,port,anchX = 5,anchY = 5):
        Thread.__init__(self)
        self.cnsQ = Queue()
        self.cns = Console(self.cnsQ)
        self.ty = ty
        self.host = host
        self.port = port
        self.id = None
        self.sock = None
        self.th_anch = None
        self.th_mob = None
        self.anchX = anchX
        self.anchY = anchY

    def run(self):
        self.cns.start()

        if self.connexion():
            self.cnsQ.put("Connexion au serveur réussie")
            if self.set_id():
                self.cnsQ.put("Id reçu : "+str(self.id))
                if self.set_type() :
                    self.cnsQ.put("Envoi du type réussi")

                    if self.ty == TYPES['TY_ANCH'] or self.ty == TYPES['TY_BOTH']:
                        self.th_anch = Anchor(self,self.anchX,self.anchY)
                        self.th_anch.start()
                    if self.ty == TYPES['TY_MOB'] or self.ty == TYPES['TY_BOTH']:
                        self.cnsQ.put("Not implemented yet")

        self.cns.join()
        self.terminate()

    def terminate(self):
        print("Arret du programme ...")
        self.cnsQ.put("quit")
        self.sock.close()
        print("Socket closed")
        print("En attente de terminaison des Threads Ancre et/ou Mobile ...")
        if self.th_anch :
            self.th_anch.terminate() #Pas sur que ça marche ...
            self.th_anch.join()
        if self.th_mob :
            self.th_mob.terminate()
            self.th_anch.join()
        print("Fin du programme.")

    def ask_id(self):
        global TYPES
        i = 0
        while i < RpiRunner.MAX_ATTEMPS :
            try:
                self.cnsQ.put("En attente de récéption de l'id ["+str(i+1)+"]")
                select.select([self.sock],[], [], RpiRunner.TIMEOUT)
            except select.error:
                pass
            else:
                msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))

                if msg.ty == TYPES['SET_ID'] :
                    self.id = int(msg.msg[0])
                    self.sock.send(message(dest=0,ty=TYPES['CNF_ID']).str())
                    return True
                else :
                    self.cnsQ.put("Message reçu non conforme : \n"+msg.toString())
            i+=1
        return False

    def set_id(self):
        global TYPES
        #On considere pour l'instant que l'ancre ou le mobile ne fait rien s'il n'as pas d'id
        self.cnsQ.put("Récuperation de l'id ...")
        while True :
            if not self.ask_id():
                self.cnsQ.put("La récuperation de l'id a échoué.")
                self.cnsQ.put("Envoi d'une nouvelle demande")
                try :
                    self.sock.send(message(dest=0,ty=TYPES['ASK_ID']).str())
                except socket.error:
                    self.cnsQ.put("Envoi impossible")
                    return False
            else :
                self.cnsQ.put("L'id a bien été récupéré : ID = "+str(id))
                return True


    def set_type(self):
        global TYPES
        i = 0
        while i<RpiRunner.MAX_ATTEMPS:
            self.cnsQ.put("En attente de demande de type ["+str(i)+"]")
            ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
            if ready[0] :
                msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                if msg.ty == TYPES['ASK_TY']:
                    try :
                        if self.ty == TYPES['TY_ANCH'] :
                            self.sock.send(message(dest=TYPES['SERV_ID'],ty=TYPES['RES_TY'], msg=TYPES['TY_ANCH']).str())
                        elif self.ty == TYPES['TY_MOB'] :
                            self.sock.send(message(dest=TYPES['SERV_ID'],ty=TYPES['RES_TY'], msg=TYPES['TY_MOB']).str())
                        elif self.ty == TYPES['TY_BOTH'] :
                            self.sock.send(message(dest=TYPES['SERV_ID'],ty=TYPES['RES_TY'], msg=TYPES['TY_BOTH']).str())
                    except socket.error :
                        return False
                    else:
                        self.cnsQ.put("En attente de confirmation de récéption ...")
                        ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
                        if ready[0] :
                            try:
                                msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                                if msg.ty == TYPES['CNF_TY'] :
                                    self.cnsQ.put("Le serveur as confirmé la récéption du type")
                            except socket.error :
                                return False
                        else:
                            self.cnsQ.put("Le serveur n'as pas confirmé la récéption du type, tant pis")
                        return True
            i+=1
        return False

    def connexion(self):
        self.cnsQ.put("Lancement du server...")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        except socket.error:
            self.cnsQ.put("Connexion impossible")
            self.cnsQ.put("quit")
            return False
        self.cnsQ.put("Connexion réussie")
        return True


class Console(Thread):
    TIMEOUT = 0.5
    def __init__(self,console_queue):
        Thread.__init__(self)
        self.queue = console_queue
        self.terminated = False

    def queueService(self):
        while not self.queue.empty():
            tmp = self.queue._get()
            if tmp.lower() in ["quit","exit"]:
                self.quit()
                return
            elif tmp.lower() in ["quitF","exitF"]:
                self.quit(empty=False)
                return
            print(tmp)

    def run(self):
        while(True):
            if self.terminated :
                return
            self.queueService()
            i, o, e = select.select( [sys.stdin], [], [], Console.TIMEOUT )
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



class Anchor(Thread):

    def __init__(self,Rpi,x,y):
        Thread.__init__(self)
        self.Rpi = Rpi
        self.ty = Rpi.ty
        self.sock = Rpi.sock
        self.id = Rpi.id
        self.cnsQ = Rpi.cnsQ
        self.x = x
        self.y = y

    def run(self):
        self.loop()

    def loop(self):
        while True :
            ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
            if ready[0] :
                msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                self.cnsQ.put("Un message a été reçu : ")

                if msg.ty == TYPES['ASK_TY']:
                    self.cnsQ.put("Demande de type reçu du client "+str(int(msg.msg[0])))
                    self.inform_type(int(msg.msg[0]))

                elif msg.ty == TYPES['ASK_DT']:
                    self.cnsQ.put("Demande d'évaluation de distance reçu du client "+str(int(msg.msg[0])))
                    self.send_dist(int(msg.msg[0]))

                elif msg.ty == TYPES['ASK_PS']:
                    self.cnsQ.put("Demande de position reçu du client "+str(int(msg.msg[0])))
                    self.send_pos(int(msg.msg[0]))

                elif msg.ty == TYPES['CNF_TY']:
                    self.cnsQ.put("Le serveur confirme qu'il as bien reçu le type")

                else :
                    self.cnsQ.put("Message incompris : "+msg.toString())

    def inform_type(self,dest):
        try :
            if self.ty == TYPES['TY_ANCH'] :
                self.sock.send(message(dest=dest,ty=TYPES['RES_TY'], msg=TYPES['TY_ANCH']).str())
            elif self.ty == TYPES['TY_MOB'] :
                self.sock.send(message(dest=dest,ty=TYPES['RES_TY'], msg=TYPES['TY_MOB']).str())
            elif self.ty == TYPES['TY_BOTH'] :
                self.sock.send(message(dest=dest,ty=TYPES['RES_TY'], msg=TYPES['TY_BOTH']).str())
        except socket.error :
            return False
        else:
            return True

    def send_dist(self,dest):
        #TODO : ...
        dist = random.uniform(3, 7) # On doit trouver 5 ?
        self.sock.send(message(dest=dest,ty=TYPES['RES_DT'],message = dist).str())

    def send_pos(self,dest):
        #TODO : ne renvoie que x pour l'instant....
        self.sock.send(message(dest=dest,ty=TYPES['RES_PS'],message = self.x).str())





rpi = RpiRunner(TYPES['TY_ANCH'],'localhost',4002)
rpi.start()

