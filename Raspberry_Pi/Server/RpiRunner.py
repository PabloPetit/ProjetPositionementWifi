import socket
import select
from queue import Queue
from threading import *
from proto import *
from avt import *
import sys
import random
import time
from math import *
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
        self.ultra = bool(ultra)
        self.dist=dist

        global TYPES


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
                        self.th_anch = Anchor(self,self.anchX,self.anchY,ultra=self.ultra, dist=self.dist,log=self.showLog)
                        self.th_anch.start()
                    if self.ty == TYPES['TY_MOB'] :
                        self.th_mob = Mobile(self,log = self.showLog)
                        self.th_mob.start()
                    elif self.ty == TYPES['TY_BOTH']:
                        self.th_mob = Mobile(self,x=self.anchX,y=self.anchY,log = self.showLog)
                        self.th_mob.start()

        self.cns.join()
        self.terminate()

    def terminate(self):

        try :
            self.sock.send(message(dest=TYPES['SERV_ID'],ty=TYPES['IM_OUT']).str())
            print("Envoi du message de sortie de réseau")
        except :
            print("Envoi impossible")
        else :
            print("Envoi réussi")

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
            self.th_mob.join()
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
            print(tmp)

    def run(self):
        while(True):
            if self.terminated :
                return
            self.queueService()
            i, o, e = select.select( [sys.stdin], [], [], Console.TIMEOUT )
            if i and not self.terminated :
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

    def __init__(self,Rpi,x,y,ultra = False, dist=None,log = False):
        Thread.__init__(self)
        self.Rpi = Rpi
        self.ty = Rpi.ty
        self.sock = Rpi.sock
        self.id = Rpi.id
        self.cnsQ = Rpi.cnsQ
        self.x = x
        self.y = y
        self.terminated = False
        self.log = log
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
            print("Nettoyage des ports GPIOs ...")
            self.ultra.terminate()

    def loop(self):
        while not self.terminated :
            try :
                ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
                if ready[0] :
                    msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                    if self.log :
                        self.cnsQ.put("Un message a été reçu : ")

                    if msg.ty == TYPES['ASK_TY']:
                        if self.log :
                            self.cnsQ.put("Demande de type reçu du client "+str(int(msg.msg[0])))
                        if not self.inform_type(int(msg.msg[0])):
                            self.terminate()
                            return

                    elif msg.ty == TYPES['ASK_ST']:
                        if self.log :
                            self.cnsQ.put("Demande d'état reçu du client "+str(int(msg.msg[0])))
                        self.send_state(int(msg.msg[0]))

                    elif msg.ty == TYPES['CNF_TY']:
                        if self.log :
                            self.cnsQ.put("Le serveur confirme qu'il as bien reçu le type")

                    else :
                        if self.log :
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

    def send_state(self,dest):

        dist = random.gauss(self.dist, 5)

        if self.ultra :
            dist = self.ultra.distance()
            #time.sleep(0.1) 

        X = encode_float(self.x)
        Y = encode_float(self.y)

        b = bytearray()
        b.append(dest)
        b.append(TYPES['RES_ST'])
        b.extend(X)
        b.extend(Y)
        b.extend(encode_float(dist))

        tmp = message(bytes=b)
        self.sock.send(tmp.str())


class Mobile(Thread):


    V_MIN = TYPES['MIN']
    V_MAX = TYPES['MAX']
    T_MIN = TYPES['TL_MIN']
    T_MAX = TYPES['TL_MAX']

    MIN_ANCH = 3

    IT_TIME = 0.2

    LOOP_TIME = 2

    def __init__(self,Rpi,x=-1,y=-1,log = False):
        Thread.__init__(self)
        self.Rpi = Rpi
        self.ty = Rpi.ty
        self.sock = Rpi.sock
        self.id = int(Rpi.id)
        self.cnsQ = Rpi.cnsQ
        self.x = x
        self.y = y
        self.log = log
        self.avtX = Avt(Mobile.V_MIN,Mobile.V_MAX,Mobile.T_MIN,Mobile.T_MAX)
        self.avtY = Avt(Mobile.V_MIN,Mobile.V_MAX,Mobile.T_MIN,Mobile.T_MAX)

        self.anch_list = {}
        self.terminated = False
        self.it = 0
        self.startTime = time.time()

    def new_anch(self,id):
        res = {}
        res['id'] = int(id)
        res['x'] = 0
        res['y'] = 0
        res['dist'] = Mobile.V_MAX
        res['avt'] = Avt(Mobile.V_MIN,Mobile.V_MAX,Mobile.T_MIN,Mobile.T_MAX)
        res['last'] = -1
        return res

    def terminate(self):
        self.terminated = True

    def run(self):
        self.cnsQ.put("Le mobile est lancé")
        self.startTime = time.time()
        self.loop()

    def loop(self):
        ite = 0
        while True :
            if time.time() - self.startTime > 1 :
                print("Nb it = "+str(ite)+" x : "+str(self.x)+" y : "+str(self.y)) 
                ite = 0
                self.startTime = time.time()
 
            nbAncre = len(self.anch_list)

            if nbAncre < Mobile.MIN_ANCH :
                self.maj_anchor_list()
                pass

            else :
                if self.trilaterate() :
                    self.send_log()
                    self.it += 1

            self.ask_for_all_states() # Mise à jour des distance de toute les ancre disponible
            ite+=1
            #time.sleep(Mobile.LOOP_TIME)


    def trilaterate(self):

        try :
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
            resY = yA+ x*ex[1] + y*ey[1]

            self.avtX.update(resX)
            self.avtY.update(resY)

            #Mise à jour
            self.x = self.avtX.currentVal
            self.y = self.avtY.currentVal
            return True

        except :
            if self.log :
                self.cnsQ.put("Trilatération impossible (probable division par 0)")
        
        return False



    def maj_anchor_list(self):
        ready = None

        try :
            if self.log :
                self.cnsQ.put("Recherche d'ancre ... ("+str(len(self.anch_list))+")")
            self.sock.send(message(dest=TYPES['SERV_ID'],ty=TYPES['ASK_AL'],msg=self.id).str())
            if self.log :
                self.cnsQ.put("En attente de récéption de la liste des ancres")
            ready = select.select([self.sock],[], [], RpiRunner.TIMEOUT)
        except select.error:
            self.cnsQ.put("Le serveur n'as pas répondu")
            pass
        except socket.error:
            self.cnsQ.put("Le serveur n'est plus en ligne")
            #TODO faire un truc
        else:

            if ready[0]:
                msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))

                if msg.ty == TYPES['RES_AL'] :

                    anch_num = int(msg.msg[0])
                    if self.log :
                        self.cnsQ.put("Nombre d'ancres reçu : "+str(anch_num))

                    anchs = [ int(msg.msg[i]) for i in range(1,anch_num+1) ]

                    toAdd = {}

                    # On supprime les ancres qui ne sont plus connéctée au serveur
                    toRemove = [ i for i in self.anch_list.values() if i['id'] not in anchs ]

                    self.anch_list = {key: value for key, value in self.anch_list.items() if value not in toRemove}

                    nb_anch = len(self.anch_list)

                    #Pour chaque id reçu, on tente une commucation et on ajoute
                    for id in anchs :

                        if nb_anch == Mobile.MIN_ANCH :
                            break

                        if id == self.id or id in self.anch_list.keys():
                            continue

                        tmp = self.new_anch(id)

                        isValid = self.ask_for_state(tmp)

                        if isValid :
                            toAdd[id] = tmp
                            nb_anch += 1

                    self.anch_list.update(toAdd)



    def ask_for_state(self,anch):

        for j in range(RpiRunner.MAX_ATTEMPS):
            try:
                msg = message(dest=anch['id'],ty=TYPES['ASK_ST'],msg=int(self.id))
                self.sock.send(msg.str())
                ready = select.select([self.sock],[],[],RpiRunner.TIMEOUT)
                if ready[0] :

                    msg = message(bytes=self.sock.recv(TYPES['BYTE_SZ']))
                    if msg.ty == TYPES['RES_ST']:
                        self.maj_anch(anch,msg.msg)
                        return True
                    else :
                        if self.log :
                            self.cnsQ.put("Message érroné : (1)\n"+msg.toString())

                else:
                    if self.log :
                        self.cnsQ.put("Pas de reponse de l'ancre "+str(anch['id'])+" aprés demande de distance")
            except socket.error:
                self.cnsQ.put("Socket error (2)")

            #time.sleep(Mobile.IT_TIME) #ya deja un time out ...

        return False


    def ask_for_all_states(self):
        #On leurs demande un par un
        global TYPES
        cmp = 0

        notValid = []

        for i in self.anch_list.values(): # Pour chaque ancre
            if cmp == Mobile.MIN_ANCH :
                break

            isValid = self.ask_for_state(i)

            if not isValid :
                notValid.append(i)

            cmp+=1

        # On supprime toute les ancres qui n'ont pas répondu
        self.anch_list = {key: value for key, value in self.anch_list.items() if value not in notValid}

    def maj_anch(self,anch,msg):

        x = decode_float(msg[0:4])
        y = decode_float(msg[4:8])
        dist = decode_float(msg[8:12])

        if self.log :
            self.cnsQ.put("Distance et position reçu de l'ancre "+str(anch['id'])+" Dist :  "+str(round(dist,2))+" x : "+str(round(x,2))+" y : "+str(round(y,2)))

        anch['last'] = dist

        anch['x'] = float(x) #TODO a remarquer qu'on ne fait d'avt sur x et y

        anch['y'] = float(y)

        anch['avt'].update(dist)

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

        if self.log : 
            self.cnsQ.put("Estimations n°"+str(self.it)+" : x = "+str(round(self.x,2))+" y = "+str(round(self.y,2))+"\n")



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
l = False
options = "ip:p:t:u:x:y:l:d"
d = 42

try :

    opt = sys.argv

    for i in range(len(opt)):

        if opt[i] in ["-ip"] :
            ip = opt[i+1]

        elif opt[i] in ["-p"] :
            port = int(opt[i+1])

        elif opt[i] in ["-t"] :
            if opt[i+1] in ["anch","ANCH","Anch"]:
                t = TYPES['TY_ANCH']
            elif opt[i+1] in ["mob","Mob","MOB"]:
                t = TYPES['TY_MOB']

        elif opt[i] in ["-x"] :
            anchX = float(opt[i+1])

        elif opt[i] in ["-y"] :
            anchY = float(opt[i+1])

        elif opt[i] in ["-u"] :
            if opt[i+1] in ["False","false","f","FALSE","F"]:
                u = False

        elif opt[i] in ["-l"] :
            if opt[i+1] in ["True","true","t","TRUE","T"]: # La prochaine fois on pensera a upper() ...
                l = True

        elif opt[i] in ["-d"] :
            d = float(opt[i+1])

    rpi = RpiRunner(t,ip,port,anchX=anchX,anchY=anchY, ultra = u,showLog=l,dist=d)
    rpi.start()
    rpi.join()


except :
    print("\nLes arguments sont incorrects : \n")
    print(helpMsg)
