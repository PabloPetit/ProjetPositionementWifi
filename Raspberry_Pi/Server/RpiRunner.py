import socket
import select
import sys
import random
import time
from queue import Queue
from threading import *
from proto import *


class RpiRunner(Thread):

    TIMEOUT = 5
    MAX_ATTEMPS = 5

    def __init__(self,ty,host,port,anchX = 5,anchY = 5,showLog = False):
        Thread.__init__(self)
        self.showLog = showLog
        self.cnsQ = Queue()
        self.cns = Console(self.cnsQ,showLog)
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
                    if self.ty == TYPES['TY_MOB'] :
                        self.th_mob = Mobile(self)
                        self.th_mob.start()
                    elif self.ty == TYPES['TY_BOTH']:
                        self.th_mob = Mobile(self,x=self.anchX,y=self.anchY)
                        self.th_mob.start()

        self.cns.join()
        self.terminate()

    def terminate(self):
        if self.showLog :
            print("Arret du programme ...")
        self.cnsQ.put("quit")
        self.sock.close()
        if self.showLog :
            print("Socket closed")
            print("En attente de terminaison des Threads Ancre et/ou Mobile ...")
        if self.th_anch :
            self.th_anch.terminate() #Pas sur que ça marche ...
            self.th_anch.join()
        if self.th_mob :
            self.th_mob.terminate()
            self.th_anch.join()
        if self.showLog :
            print("Fin du programme.")

    def ask_id(self):
        global TYPES
        i = 0
        while i < RpiRunner.MAX_ATTEMPS :
            ready = False
            try:
                self.cnsQ.put("En attente de récéption de l'id ["+str(i+1)+"]")
                ready = select.select([self.sock],[], [], RpiRunner.TIMEOUT)
            except select.error:
                self.cnsQ.put("Socket error (4)")
                self.terminate()
                pass
            if ready[0]:
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
                self.cnsQ.put("L'id a bien été récupéré : ID = "+str(self.id))
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
    def __init__(self,console_queue,showLog):
        Thread.__init__(self)
        self.showLog = showLog
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
            if self.showLog :
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
        if self.showLog :
            print("La console a été coupée")
        if empty :
            if self.showLog :
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
        self.terminated = False

    def run(self):
        self.cnsQ.put("L'ancre est lancée")
        self.loop()

    def terminate(self):
        self.terminated = True

    def loop(self):
        while not self.terminated :
            ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
            if ready[0] :
                msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                self.cnsQ.put("Un message a été reçu : ")

                if msg.ty == TYPES['ASK_TY']:
                    self.cnsQ.put("Demande de type reçu du client "+str(int(msg.msg[0])))
                    if not self.inform_type(int(msg.msg[0])):
                        self.terminate()
                        return

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
        dist = random.uniform(3, 7)

        bts = floatToRawLongBits(dist)
        self.sock.send(message(dest=dest,ty=TYPES['RES_DT'],message = bts).str())

    def send_pos(self,dest):
        #TODO : ...
        mess = floatToRawLongBits(self.x).append(floatToRawLongBits(self.y))#j'y crois pas trop
        self.sock.send(message(dest=dest,ty=TYPES['RES_PS'],message = self.x).str())


class Mobile(Thread):

    V_MIN = 0
    V_MAX = 100
    MIN_ANCH = 3

    def __init__(self,Rpi,x=None,y=None):
        Thread.__init__(self)
        self.Rpi = Rpi
        self.ty = Rpi.ty
        self.sock = Rpi.sock
        self.id = Rpi.id
        self.cnsQ = Rpi.cnsQ
        self.x = x
        self.y = y
        self.anch_list = {}
        self.terminated = False

    def new_anch(self,id):
        res = {}
        res['id'] = int(id)
        res['x'] = Mobile.V_MIN
        res['y'] = Mobile.V_MIN
        res['dist'] = Mobile.V_MIN
        return res

    def run(self):
        self.cnsQ.put("Le mobile est lancé")
        self.find_anchors()
        self.loop()

    def terminate(self):
        self.terminated = True

    def loop(self):
        while not self.terminated :
            if len(self.anch_list) <Mobile.MIN_ANCH :
                self.find_anchors()

            self.ask_for_distance()

            self.triangulate()

    def triangulate(self):
        # Faire la triangulation
        pass

    def maj_anch(self,i,dist):
        #Reçoit un float et un indice

        anch = self.anch_list[i]

        if dist > anch['dist']:
            #Adjust +
            pass
        elif dist < anch['dist']:
            #adjust -
            pass
        else :
            # OK
            pass


    def ask_for_distance(self):
        #On leurs demande un par un
        global TYPES
        for i in range(0,min(len(self.anch_list),Mobile.MIN_ANCH)):
            try:
                self.sock.send(message(dest=self.anch_list[i]['id'],ty=TYPES['ASK_DT'],msg = self.id).str())
                ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
                if ready[0] :
                    try :
                        msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                        if msg.ty == TYPES['RES_DT']:
                            self.maj_anch(i,longBitsToFloat(msg.msg))
                        else :
                            self.cnsQ.put("Message érroné")
                    except socket.error :
                        self.cnsQ.put("Socket error (3)")
                        return False
                else:
                    self.cnsQ.put("Pas de reponse") #Message a changer
            except socket.error:
                self.cnsQ.put("Socket error (2)")



    def find_anchors(self):
        global TYPES
        while not len(self.anch_list) >= Mobile.MIN_ANCH :
            ready = None
            try :
                self.cnsQ.put("Recherche d'ancre ... ("+str(len(self.anch_list))+")")
                self.sock.send(message(dest=TYPES['SERV_ID'],ty=TYPES['ASK_AL'],msg=self.id).str())
                self.cnsQ.put("En attente de récéption de la liste des ancres")
                ready = select.select([self.sock],[], [], RpiRunner.TIMEOUT)
            except select.error:
                self.cnsQ.put("Socket error (5 ?)")
                return False
                pass
            except socket.error:
                self.cnsQ.put("Socket error (1)")
                return False
            else:
                if ready[0]:
                    msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                    if msg.ty == TYPES['RES_AL'] :
                        anch_num = int(msg.msg[0])
                        self.cnsQ.put("Liste d'ancre reçu : "+str(anch_num))
                        tmp = {}
                        for i in range(1,anch_num+1) :
                            if int(msg.msg[i]) != id :
                                try :
                                    tmp[int(msg.msg[i])] = self.new_anch(int(msg.msg[i]))
                                except ValueError:
                                    self.cnsQ.put("Message corrompu")
                                    break
                        self.cnsQ.put("Liste des ancres récupérée : \n"+str(tmp))
                        for i in tmp.values():
                            if i['id'] not in self.anch_list.keys():
                                self.anch_list.update(tmp)
        return True



a1 = RpiRunner(TYPES['TY_ANCH'],'localhost',4002)
a2 = RpiRunner(TYPES['TY_ANCH'],'localhost',4002)
a3 = RpiRunner(TYPES['TY_ANCH'],'localhost',4002)
a4 = RpiRunner(TYPES['TY_ANCH'],'localhost',4002)


a1.start()
a2.start()
a3.start()
a4.start()


rpi = RpiRunner(TYPES['TY_MOB'],'localhost',4002, showLog=True)
rpi.start()