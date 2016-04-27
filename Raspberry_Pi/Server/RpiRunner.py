import socket
import select
from queue import Queue
from threading import *
from proto import *
from avt import *
from math import *
import sys
import random

try:
    from ultra import *
except :
    print("Rpi.GPIO introuvable")



class RpiRunner(Thread):

    TIMEOUT = 5
    MAX_ATTEMPS = 5

    def __init__(self,ty,host,port,anchX = 5,anchY = 6,showLog = False, ultra = False, dist=42):
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
        self.ultra = ultra
        self.dist=dist

        global TYPES

        if self.showLog :

            if self.ty == TYPES['TY_ANCH'] :
                print("L'ancre est lancée")

            print("Addresse : "+str(self.host))
            print("Port : "+str(self.port))
            print("X = "+str(self.anchX))
            print("Y = "+str(self.anchY))
            print("Ultra : "+str(self.ultra))
            print("Dist : "+str(self.dist))

    def run(self):
        self.cns.start()

        if self.connexion():
            self.cnsQ.put("Connexion au serveur réussie")
            if self.set_id():
                self.cnsQ.put("Id reçu : "+str(self.id))
                if self.set_type() :
                    self.cnsQ.put("Envoi du type réussi")
                    if self.ty == TYPES['TY_ANCH'] or self.ty == TYPES['TY_BOTH']:
                        self.th_anch = Anchor(self,self.anchX,self.anchY,ultra=self.ultra, dist=self.dist)
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
                    #self.sock.send(message(dest=['SERV_ID'],ty=TYPES['CNF_ID']).str())
                    self.sock.send(message(dest=TYPES['SERV_ID'],ty=TYPES['CNF_ID']).str())
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
        self.cnsQ.put("Connexion en cours ...")
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

    def __init__(self,Rpi,x,y,ultra = False, dist=None):
        Thread.__init__(self)
        self.Rpi = Rpi
        self.ty = Rpi.ty
        self.sock = Rpi.sock
        self.id = Rpi.id
        self.cnsQ = Rpi.cnsQ
        self.x = x
        self.y = y
        self.terminated = False
        self.ultra = ultra
        self.dist = dist
        if self.ultra:
            self.ultra = Ultra()

    def run(self):
        self.cnsQ.put("L'ancre est lancée")
        self.loop()

    def terminate(self):
        self.terminated = True
        if self.ultra :
            self.ultra.terminate()

    def loop(self):
        while not self.terminated :
            try :
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
            except select.error :
                self.cnsQ.put("Socket error (6)")
                return

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

        dist = random.gauss(self.dist, 5)

        if self.ultra :
            dist = self.ultra.distance()
        self.cnsQ.put("dist calcule" + str(dist))

        mess = encode_float(dist)

        b = bytearray()
        b.append(dest)
        b.append(TYPES['RES_DT'])
        b.extend(mess)

        tmp = message(bytes=b)

        self.sock.send(tmp.str())

    def send_pos(self,dest):

        X = encode_float(self.x)
        Y = encode_float(self.y)

        b = bytearray()
        b.append(dest)
        b.append(TYPES['RES_PS'])
        b.extend(X)
        b.extend(Y)

        tmp = message(bytes=b)
        self.sock.send(tmp.str())


class Mobile(Thread):


    V_MIN = TYPES['MIN']
    V_MAX = TYPES['MAX']
    T_MIN = TYPES['TL_MIN']
    T_MAX = TYPES['TL_MAX']

    MIN_ANCH = 3

    IT_TIME = 0.2

    def __init__(self,Rpi,x=-1,y=-1):
        Thread.__init__(self)
        self.Rpi = Rpi
        self.ty = Rpi.ty
        self.sock = Rpi.sock
        self.id = int(Rpi.id)
        self.cnsQ = Rpi.cnsQ
        self.x = x
        self.y = y

        self.avtX = Avt(Mobile.V_MIN,Mobile.V_MAX,Mobile.T_MIN,Mobile.T_MAX)
        self.avtY = Avt(Mobile.V_MIN,Mobile.V_MAX,Mobile.T_MIN,Mobile.T_MAX)
        self.anch_list = {}
        self.terminated = False
        self.it = 0

    def new_anch(self,id):
        res = {}
        res['id'] = int(id)
        res['x'] = 0
        res['y'] = 0
        res['dist'] = Mobile.V_MAX
        res['avt'] = Avt(Mobile.V_MIN,Mobile.V_MAX,Mobile.T_MIN,Mobile.T_MAX)
        res['last'] = -1
        return res

    def run(self):
        self.cnsQ.put("Le mobile est lancé")
        self.set_anchor_list()
        self.loop()

    def terminate(self):
        self.terminated = True

    def send_log(self):

        b = bytearray()
        b.append(TYPES['SERV_ID'])
        b.append(TYPES['RES_LG'])


        b.extend(encode_float(self.x))
        b.extend(encode_float(self.y))

        cmp = 0
        for i in self.anch_list.values():
            if cmp == Mobile.MIN_ANCH :
                break
            b.extend(encode_float(i['avt'].currentVal))
            b.extend(encode_float(i['last']))
            cmp += 1

        b.extend(encode_float(self.it))

        tmp = message(bytes=b)

        self.sock.send(tmp.str())

    def loop(self):
        while not self.terminated :
            if len(self.anch_list) <Mobile.MIN_ANCH :
                self.find_anchors()

            self.ask_for_distance()

            # self.trilaterate()

            self.send_log()

            self.it += 1

    def trilaterate(self):
        cmp = 0
        anchs = []
        for i in self.anch_list.values():
            if cmp == Mobile.MIN_ANCH :
                break
            anchs.append(i)

        A = anchs[0]
        B = anchs[1]
        C = anchs[2]

        xA = A['x']
        yA = A['y']
        dA = A['avt'].currentVal
        xB = B['x']
        yB = B['y']
        dB = B['avt'].currentVal
        xC = C['x']
        yC = C['y']
        dC = C['avt'].currentVal

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
        resY = xA+ x*ex[1] + y*ey[1]

        self.avtX.update(resX)
        self.avtY.update(resY)
        self.x = self.avtX.currentVal
        self.y = self.avtY.currentVal


    def maj_anch(self,anch,msg):

        dist = decode_float(msg[0:4])

        self.cnsQ.put("Distance reçu de l'ancre "+str(anch['id'])+" : "+str(dist))

        anch['last'] = dist

        anch['avt'].update(dist)

    def set_anchor_position(self,anch,msg):
        x = decode_float(msg[0:4])
        y = decode_float(msg[4:8])
        anch['x'] = x
        anch['y'] = y

        self.cnsQ.put("Position de l'ancre "+str(anch['id'])+" reçu :  x = "+str(x)+" y = "+str(y))

    def ask_position(self,anch):
        global TYPES
        cmp = 0
        while cmp < 5 : # BARBARE

            try:
                msg = message(dest=anch['id'],ty=TYPES['ASK_PS'],msg=int(self.id))
                self.sock.send(msg.str())
                ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
                if ready[0] :
                    try :
                        msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                        if msg.ty == TYPES['RES_PS']:
                            self.set_anchor_position(anch,msg.msg)
                            return True
                        else :
                            self.cnsQ.put("Message érroné : (2)\n"+msg.toString())
                            return False
                    except socket.error :
                        self.cnsQ.put("Socket error (3)")
                        return False
                else:
                    self.cnsQ.put("Pas de reponse") #Message a changer
            except socket.error:
                self.cnsQ.put("Socket error (2)")
                return False
            cmp+=1

        return False


    def ask_for_distance(self):
        #On leurs demande un par un
        global TYPES
        cmp = 0
        for i in self.anch_list.values():
            if cmp == Mobile.MIN_ANCH :
                break
            try:
                msg = message(dest=i['id'],ty=TYPES['ASK_DT'],msg=int(self.id))
                self.sock.send(msg.str())
                ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
                if ready[0] :
                    try :
                        msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                        if msg.ty == TYPES['RES_DT']:
                            self.maj_anch(i,msg.msg)
                        else :
                            self.cnsQ.put("Message érroné : (1)\n"+msg.toString())
                    except socket.error :
                        self.cnsQ.put("Socket error (3)")
                        return False
                else:
                    self.cnsQ.put("Pas de reponse") #Message a changer
            except socket.error:
                self.cnsQ.put("Socket error (2)")
            time.sleep(Mobile.IT_TIME)
            cmp+=1

    def set_anchor_list(self):
        global TYPES

        while not len(self.anch_list) >= Mobile.MIN_ANCH:

            self.find_anchors()
            tmp = []
            for i in self.anch_list :
                j = 0
                ok = False
                while j < RpiRunner.MAX_ATTEMPS :
                    if self.ask_position(self.anch_list[i]) :
                        ok = True
                        break
                    j+=1
                if not ok :
                    tmp.append(self.anch_list[i])

            self.anch_list = {key: value for key, value in self.anch_list.items() if value not in tmp}
            time.sleep(Mobile.IT_TIME)


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


helpMsg = "Options : \n" \
       "    -ip <adresse>\n" \
       "    -p <port\n" \
       "    -t <type> (anch/mob)\n" \
       "    -u <ultra> (True/False)\n" \
       "    -x <position>\n" \
       "    -y <position>\n" \
        "   -l <log> (True/False)\n" \
          "    -d <distance>"


ip = "localhost"
port = 4000
t = TYPES['TY_ANCH']
anchX = 1
anchY = 1
u = True
l = True
options = "ip:p:t:u:x:y:l:d"
d = 42

try :

    opt = sys.argv

    for i in range(len(opt)):

        if opt[i] in ["-ip"] :
            ip = opt[i+1]

        elif opt[i] in ["-p"] :
            p = opt[i+1]

        elif opt[i] in ["-t"] :
            if opt[i+1] in ["anch","ANCH","Anch"]:
                t = TYPES['TY_ANCH']
            elif opt[i+1] in ["mob","Mob","MOB"]:
                t = TYPES['TY_MOB']

        elif opt[i] in ["-x"] :
            anchX = opt[i+1]

        elif opt[i] in ["-y"] :
            anchY = opt[i+1]

        elif opt[i] in ["-u"] :
            if opt[i+1] in ["False","false","f","FALSE","F"]:
                u = False

        elif opt[i] in ["-l"] :
            if opt[i+1] in ["False","false","f","FALSE","F"]:
                l = False

        elif opt[i] in ["-d"] :
            d = opt[i+1]

    rpi = RpiRunner(t,ip,port,anchX=anchX,anchY=anchY, ultra = u,showLog=l,dist=d)
    rpi.start()
    rpi.join()


except :
    print("\nLes arguments sont incorrects : \n")
    print(helpMsg)













