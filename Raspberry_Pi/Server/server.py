import socket
import select
from queue import Queue
from threading import *
from proto import *
from time import *

import sys


server_id = TYPES['SERV_ID'] #Le server à toujours pour id 1
anchor_list = [] #Liste des ancres connectées
mobile_list = [] #Liste des mobiles connecté
client_list = [] #Liste des thread client

server_th = None # Thread qui gère le server
console_th = None # Thread qui gère la console

console_queue = Queue()

terminated = False

"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ MAIN @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""

def main(ip="localhost",port=4002,maxQueue=5,printRtr = False):

    print("Ip : "+str(ip))
    print("Port "+str(port))

    print("Lancement du serveur ...")

    console_th = console()

    server_th = server(ip,port,maxQueue,printRtr=printRtr)

    console_th.start()
    server_th.start()

    console_th.join()
    server_th.join()

    print("Fin du programme")


"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ CONSOLE @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""

class console(Thread):

    global TYPES
    TIMEOUT = 5

    def __init__(self):
        Thread.__init__(self)
        self.queue = console_queue

    def queueService(self):
        while not self.queue.empty():
            tmp = self.queue._get()
            if tmp.lower() in ["quit","exit"]:
                self.quit()
                return
            print(tmp)

    def run(self):
        global terminated
        sleep(0.5)
        while(True):
            if terminated :
                return
            self.queueService()
            i, o, e = select.select( [sys.stdin], [], [], console.TIMEOUT)
            if i and not terminated: # Test
                st = sys.stdin.readline().strip()
                if st.lower() in ["exit","quit"]:
                    self.quit()
                elif st.lower() in ["quitF","exitF"]:
                    self.quit(empty=False)
                elif st.lower() in ["list_m"]:
                    print("Liste des mobile")
                    print(mobile_list)
                elif st.lower() in ["list_a"]:
                    print("Liste des ancre")
                    print(anchor_list)
                elif st.lower() in ["state"]:
                    print("Etat global du server")
                    print("Fonction non implémentée")
                elif st.lower() in ["reboot_server"]:
                    print("Relance le server")
                    print("Fonction non implémentée")
                elif st.lower() in ["send_msg"]:
                    print("Envoi un message à un mobile")
                    print("Fonction non implémentée")
                elif st.lower() in ["log"]:
                    self.log()
                else:
                    print("Commande inconnue")


    def log(self):
        print("Voici la liste des mobiles connécté : ")
        print([i.id for i in mobile_list])
        i = input("Veuiller choisir un id : \n")
        if not i.isdigit() :
            print("Id inccorecte")
            return
        i = int(i)
        id = [j for j in client_list if j.client.id==i]

        if len(id)>0:
            mob = id[0]
            cmd = input("Voulez-vous : \n"
                  "1/ Afficher le log en console\n"
                  "2/ Enregistrer le log\n")

            if not cmd.isdigit():
                return

            cmd = int(cmd)

            if cmd == 1 :
                print(mob.get_log())

            elif cmd == 2 :
                cmd = input("Entrez le nom du fichier : \n> ")
                try :
               	    fichier = open(cmd, "w")
                    fichier.write(mob.get_log())
                    fichier.close()
                    print("Le fichier a bien été sauvegardé")
                    sleep(2)
                except:
                    print("Ouverture impossible, abandon")
                    sleep(2)
                    pass
                pass
        else:
            print("Identifiant incorrect")



    def quit(self, empty = True):
        global terminated
        terminated = True
        print("La console a été coupée")
        if empty :
            print("Vidage de la file console :")
            self.queueService()


"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ SERVEUR @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""


class server(Thread):

    TIMEOUT = 2

    def __init__(self, ip,port,maxQueue,printRtr=True):
        Thread.__init__(self)
        self.sock = None
        self.port = port
        self.maxQueue = maxQueue
        self.id_cnt = 2
        self.ip = ip
        self.printRtr = printRtr
        socket.setdefaulttimeout(server.TIMEOUT)

    def run(self):
        global terminated
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.ip,self.port))
            self.sock.listen(self.maxQueue)
        except socket.error:
            console_queue.put("Connexion refusée.\nLe serveur n'as pas put être lancé.")
            console_queue.put("quit")
            return

        console_queue.put("Le server est en ligne. IP = "+str(self.sock.getsockname()[0])+" Port  = "+str(self.sock.getsockname()[1]))

        while not terminated:
            try :
                sock,info = self.sock.accept()
            except :
                continue
            console_queue.put("Un nouveau client client s'est connecté : ip : "+str(info[0])+" port : "+str(info[1]))
            self.client = client(sock,info, self.id_cnt)
            self.id_cnt+=1
            nw_client = thread_client(self.client,printRtr=self.printRtr)
            client_list.append(nw_client)
            nw_client.start()

        print("Le Serveur n'est plus en ligne")




"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ THREAD CLIENT @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""

class thread_client(Thread):

    MAX_ATTEMPS = 5 #Nombre de repetition pour les communication
    TIMEOUT = 5 #Temps d'attente d'une reponse

    def __init__(self, client,printRtr=True):
        Thread.__init__(self)
        self.client = client
        self.terminated = False
        self.log = []
        self.printRtr = printRtr



    def close_connexion(self, pb = True):
        global TYPES
        global anchor_list
        global mobile_list
        global client_list

        if pb :
            console_queue.put("Probleme de connexion avec le client "+str(self.client.id))
            console_queue.put("Fermeture de la connexion ...")

        self.client.sock.close()

        try :
            client_list.remove(self)
            if self.client.ty == TYPES['TY_ANCH'] :
                anchor_list.remove(self.client)
            elif self.client.ty == TYPES['TY_MOB'] :
                mobile_list.remove(self.client)
            elif self.client.ty == TYPES['TY_BOTH'] :
                anchor_list.remove(self.client)
                mobile_list.remove(self.client)
        except ValueError :
            console_queue.put("Problème de remove")
            pass

        self.terminated = True
        console_queue.put("Connection terminée avec le client : "+str(self.client.id))

    def run(self):
        # 1 : on donne son id au client
        if not self.set_client_id() :
            console_queue.put("Le client "+str(self.client.id)+" ne repond pas, déconnexion")
            self.close_connexion(pb = False)
            return
        else :
            console_queue.put("Le client "+str(self.client.id)+" à confirmé son id")

        if not self.ask_ty():
            console_queue.put("Le client "+str(self.client.id)+" n'as pas confirmé son type, déconnexion")
            self.close_connexion(pb = False)
            return

        console_queue.put("Lancement de la boucle de communication avec le client : "+str(self.client.id))
        self.loop()

    def set_client_id(self):
        i=0
        global TYPES

        console_queue.put("Envoi de l'id au client "+str(self.client.id))
        while(i<self.MAX_ATTEMPS): #On vas tenter plusieurs fois de communiquer avec le client, apres quoi on fermera la sock si pas de reponse
            try:
                if self.printRtr :
                    console_queue.put("Envoi d'id, essai numero "+str(i)+" vers le client "+str(self.client.id))
                self.client.sock.send(message(dest=self.client.id, ty=TYPES['SET_ID'], msg=self.client.id).str()) # Envoi au nouveau client son id
                if self.printRtr :
                    console_queue.put("En attente de confirmation id - client "+str(self.client.id)+" ...")
                ready = select.select([self.client.sock],[], [], thread_client.TIMEOUT)

                if ready[0] :
                    msg = message(bytes=self.client.sock.recv(TYPES['BYTE_SZ']))
                    if msg.ty == TYPES['CNF_ID']:
                        return True
                    else:
                        if self.printRtr :
                            console_queue.put("Message incorrect reçu - client"+str(self.client.id))
                            console_queue.put(msg.toString())

            except select.error:
                print("ERROR")
                pass
            except socket.error as e:
                return False
            i+=1
        return False

    def new_id(self): #TODO redefinir ce que fait cette fonction, inutil de retirer le client des liste si c'est pour lui rendre la meme id
        if self.client.ty == TYPES['TY_ANCH'] :
            anchor_list.remove(self.client)
        elif self.client.ty == TYPES['TY_MOB'] :
            mobile_list.remove(self.client)
        elif self.client.ty == TYPES['TY_BOTH'] :
            anchor_list.remove(self.client)
            mobile_list.remove(self.client)

        self.set_client_id()

    def ask_ty(self):
        global TYPES
        global server_id
        i=0
        if self.printRtr :
            console_queue.put("Demande de type envoyé au client "+str(self.client.id))
        while(i<thread_client.MAX_ATTEMPS):
            console_queue.put("Envoi demande de confirmation type numero "+str(i)+" vers le client "+str(self.client.id))
            try:

                mess = message(dest=self.client.id, ty=TYPES['ASK_TY'], msg=server_id).str()

                self.client.sock.send(mess) # Demande son type au client
                if self.printRtr :
                    console_queue.put("En attente de réponse - client "+str(self.client.id)+" ...")
                ready = select.select([self.client.sock],[], [], thread_client.TIMEOUT)
                if ready[0] :
                    data = self.client.sock.recv(TYPES['BYTE_SZ'])
                    data = bytearray(data)
                    msg = message(bytes=data)
                    ty = int(msg.msg[0])
                    ok = False
                    if ty == TYPES['TY_ANCH'] :
                        console_queue.put("Le client "+str(self.client.id)+" est une ancre")
                        anchor_list.append(self.client)
                        self.client.ty = TYPES['TY_ANCH']
                        ok =  True;
                    elif ty == TYPES['TY_MOB'] :
                        console_queue.put("Le client "+str(self.client.id)+" est un mobile")
                        mobile_list.append(self.client)
                        self.client.ty = TYPES['TY_MOB']
                        ok =  True
                    elif ty == TYPES['TY_BOTH'] :
                        console_queue.put("Le client "+str(self.client.id)+" est une ancre et un mobile")
                        anchor_list.append(self.client)
                        mobile_list.append(self.client)
                        self.client.ty = TYPES['TY_BOTH']
                        ok =  True
                    if ok :
                        self.client.sock.send(message(dest=self.client.id, ty=TYPES['CNF_TY']).str())
                        return True

            except socket.error:
                return False
            except ValueError:
                console_queue.put("Message incorrect")
                pass
            i+=1
        return False

    def send_anchor_list(self):

        tmp = []
        tmp.append(int(min(TYPES['MSG_LN'],len(anchor_list))))

        for i in range(0,min(TYPES['MSG_LN'],len(anchor_list))):
            tmp.append(anchor_list[i].id)

        try:
            self.client.sock.send(message(dest=self.client.id, ty=TYPES['RES_AL'], msg=tmp).str())
        except socket.error:
                    self.close_connexion()



    def maj_log(self,msg):

        try :
            x = decode_float(msg.msg[0:4]) # 0
            y = decode_float(msg.msg[4:8]) # 1
            dt1 = decode_float(msg.msg[8:12]) # 2
            sg1 = decode_float(msg.msg[12:16]) # 3
            dt2 = decode_float(msg.msg[16:20]) # 4
            sg2 = decode_float(msg.msg[20:24]) # 5
            dt3 = decode_float(msg.msg[24:28]) # 6
            sg3 = decode_float(msg.msg[28:32]) # 7
            it = decode_float(msg.msg[32:36]) # 8

            tmp = (x,y,dt1,sg1,dt2,sg2,dt3,sg3,it)
            self.log.append(tmp)



        except :
            console_queue.put("Log illisible : \n"+msg.toString())
            return


    def get_log(self):
        st = ""
        for i in self.log :
            st+=str(i[0])+" "+str(i[1])+" "+str(i[2])+" "+str(i[3])+" "+str(i[4])+" "+str(i[5])+" "+str(i[6])+" "+str(i[7])+" "+str(i[8])+"\n"

        return st


    def loop(self):
        global mobile_list
        global anchor_list
        global TYPES
        global terminated
        #Boucle de communication
        while not self.terminated and not terminated:
            ready = None
            try:
                ready = select.select([self.client.sock],[], [], thread_client.TIMEOUT)

                if ready[0] :
                    msg = message(bytes=bytearray(self.client.sock.recv(TYPES['BYTE_SZ'])))
                    if msg.dest == 0:
                        continue;
                    if msg.dest > TYPES['SERV_ID'] :
                        sent = False
                        for mob in mobile_list :
                            if mob.id == msg.dest :
                                mob.sock.send(msg.str())
                                sent = True
                                break

                        if not sent :
                            for mob in anchor_list :
                                if mob.id == msg.dest :
                                    mob.sock.send(msg.str())
                                    sent = True
                                    break

                        if sent :
                            if self.printRtr :
                                console_queue.put("Message du client "+str(self.client.id)+" à été retransmit vers le client "+str(msg.dest))
                        else:
                            if self.printRtr :
                                console_queue.put("Le message du client "+str(self.client.id)+" n'as pas trouvé de destinataire\n"+msg.toString())
                            try:
                                self.client.sock.send(message(dest=self.client.id, ty=TYPES['UNK_ID'],msg=msg.dest).str())
                            except socket.error:
                                self.close_connexion()


                    else :
                        if self.printRtr :
                            console_queue.put("Le message demande à être traité par le serveur")

                        if msg.ty == TYPES['ASK_ID'] :
                            if self.printRtr :
                                console_queue.put("Demande d'id reçu du client "+str(self.client.id))
                            self.new_id()
                        elif msg.ty == TYPES['ASK_AL']:
                            if self.printRtr :
                                console_queue.put("Demande de liste des ancres reçu du client "+str(self.client.id))
                            self.send_anchor_list()
                        elif msg.ty == TYPES['RES_LG']:
                            if self.printRtr :
                                console_queue.put("Log reçu du client "+str(self.client.id))
                            self.maj_log(msg)
                        elif msg.ty == TYPES['IM_OUT']:
                            if self.printRtr :
                                console_queue.put("Le client "+str(self.client.id)+" annoce sa sortie du réseaux")
                            self.close_connexion()
                            #console_queue.put(msg.toString())
                        else:
                            if self.printRtr :
                                console_queue.put("Demande incomprise du client "+str(self.client.id))
                            console_queue.put(msg.toString())

            except :
                self.close_connexion()
                return





helpMsg = "Options : \n" \
       "    -ip <adresse>\n" \
       "    -p <port>\n" \
       "    -l <retransmission> (True/False)\n" \
          "    -mxQ <max queue>"


ip = "192.168.43.7"
port = 4000
mxQ = 5
rtr = False

options = "ip:p:rtr:mxQ"

try :

    opt = sys.argv

    for i in range(len(opt)):

        if opt[i] in ["-ip"] :
            ip = opt[i+1]

        elif opt[i] in ["-p"] :
            port = opt[i+1]


        elif opt[i] in ["-l"] :
            if opt[i+1] in ["True","TRUE","t","true","T"]:
                rtr = True

        elif opt[i] in ["-mxQ"] :
            mxQ = opt[i+1]


    main(ip,int(port),maxQueue=int(mxQ),printRtr=rtr)


except :
    print("\nLes arguments sont incorrects : \n")
    print(helpMsg)



