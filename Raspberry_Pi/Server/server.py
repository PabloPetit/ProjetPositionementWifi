import socket
import time
import select
from queue import Queue
from threading import *
from proto import *
import sys


server_id = 0 #Le server à toujours pour id 0
anchor_list = [] #Liste des ancres connectées
mobile_list = [] #Liste des mobiles connecté
client_list = [] #Liste des thread client

server_th = None # Thread qui gère le server
console_th = None # Thread qui gère la console

console_queue = Queue()

"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ MAIN @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""

def main():

    print("Lancement du serveur ...")

    console_th = console()
    server_th = server(4013,5)

    console_th.start()
    server_th.start()


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
                elif st.lower() in ["list_m"]:
                    print("Liste des mobile")
                    print(mobile_list)
                elif st.lower() in ["list_a"]:
                    print("Liste des ancre")
                    print(anchor_list)
                elif st.lower() in ["state"]:
                    print("Etat global du server")
                elif st.lower() in ["reboot_server"]:
                    print("Relance le server")
                elif st.lower() in ["send_msg"]:
                    print("Envoi un message à un mobile")

    def quit(self, empty = True):
        self.terminated = True
        print("La console a été coupée")
        if empty :
            print("Vidage de la file :")
            self.queueService()


"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ SERVEUR @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""


class server(Thread):
    def __init__(self, port, maxQueue, console_queue=None):
        Thread.__init__(self)
        self.sock = None
        self.port = port
        self.maxQueue = maxQueue
        self.console_queue = console_queue
        self.id_cnt = 1
    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('',self.port))
        self.sock.listen(self.maxQueue)
        console_queue.put("Le server est en ligne. IP = "+str(self.sock.getsockname()[0])+" Port  = "+str(self.sock.getsockname()[1]))

        while(True):
            sock,info = self.sock.accept()
            console_queue.put("Un nouveau client client s'est connecté : ip : "+str(info[0])+" port : "+str(info[1]))
            self.client = client(sock,info, self.id_cnt)
            self.id_cnt+=1
            nw_client = thread_client(self.client)
            client_list.append(nw_client)
            nw_client.start()




"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ THREAD CLIENT @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""

class thread_client(Thread):

    MAX_ATTEMPS = 5 #Nombre de repetition pour les communication
    TIMEOUT = 5 #Temps d'attente d'une reponse

    def __init__(self, client):
        Thread.__init__(self)
        self.client = client
        self.terminated = False

    def close_connexion(self):
        global TYPES
        self.client.sock.close()
        client_list.remove(self)
        if self.client.ty == TYPES['TY_ANCH'] :
            anchor_list.remove(client)
        elif self.client.ty == TYPES['TY_MOB'] :
            mobile_list.remove(client)
        elif self.client.ty == TYPES['TY_BOTH'] :
            anchor_list.remove(client)
            mobile_list.remove(client)
        self.terminated = True

    def run(self):
        # 1 : on donne son id au client
        if not self.set_client_id() :
            console_queue.put("Le client "+str(self.client.sock.getsockname())+" ne repond pas, déconnexion")
            self.close_connexion()
        else :
            console_queue.put("Le client "+str(self.client.id)+" à confirmé son id")

        if not self.ask_ty():
            console_queue.put("Le client "+str(self.client.sock.getsockname())+" a repondu un code erroné, deconnexion")
            self.close_connexion()

        console_queue.put("Lancement de la boucle de communication avec le client : "+str(self.client.id))
        self.loop()

    def set_client_id(self):
        i=0
        global TYPES
        console_queue.put("Envoi de l'id au client "+str(self.client.id))
        while(i<self.MAX_ATTEMPS): #On vas tenter plusieurs fois de communiquer avec le client, apres quoi on fermera la sock si pas de reponse
            self.client.sock.send(message(dest=self.client.id, ty=TYPES['SET_ID'], msg=self.client.id).str()) # Envoi au nouveau client son id
            try:
                select.select([self.client.sock],[], [], thread_client.TIMEOUT)
            except select.error:
                pass
            else:
                msg = message(string=self.client.sock.recv(TYPES['BYTE_SZ']).decode())#MESSAGE
                if msg.ty == TYPES['CNF_ID']:
                    return True
            i+=1
        return False

    def new_id(self):
        if self.client.ty == TYPES['TY_ANCH'] :
            anchor_list.remove(client)
        elif self.client.ty == TYPES['TY_MOB'] :
            mobile_list.remove(client)
        elif self.client.ty == TYPES['TY_BOTH'] :
            anchor_list.remove(client)
            mobile_list.remove(client)

        self.set_client_id()

    def ask_ty(self):
        global TYPES
        i=0
        while(i<thread_client.MAX_ATTEMPS):
            self.client.sock.send(message(dest=self.client.id, ty=TYPES['ASK_TY'], msg=server_id).str()) # Demande son type au client
            to_read = []
            try:
                to_read, wlist, xlist = select.select([self.client.sock],[], [], thread_client.TIMEOUT)
            except select.error:
                pass
            else:
                msg = message(string=self.client.sock.recv(TYPES['BYTE_SZ']).decode())
                ty = int(msg.msg)
                if ty == TYPES['TY_ANCH'] :
                    console_queue.put("Le client "+str(self.client.id)+" est une ancre")
                    anchor_list.append(self.client)
                    return True;
                elif ty == TYPES['TY_MOB'] :
                    console_queue.put("Le client "+str(self.client.id)+" est un mobile")
                    mobile_list.append(self.client)
                    return True
                elif ty == TYPES['TY_BOTH'] :
                    console_queue.put("Le client "+str(self.client.id)+" est une ancre et un mobile")
                    anchor_list.append(self.client)
                    mobile_list.append(self.client)
                    return True
            i+=1
        return False

    def send_anchor_list(self):

        message = ""

        for i in range(0,max(TYPES['MSG_LN'],len(anchor_list))):
            message+=anchor_list[i].id #TODO : a tester

        self.client.sock.send(message(dest=self.client.id, ty=TYPES['RES_AL'], msg=message).str())

    def loop(self):
        global mobile_list
        global anchor_list
        #Boucle de communication
        if self.terminated :
            return

        try:
            select.select([self.client.sock],[], [], thread_client.TIMEOUT)
        except select.error:
            pass
        else :
            msg = message(string=self.client.sock.recv(TYPES['BYTE_SZ']).decode())

            if msg.dest != 0 :
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
                    console_queue.put("Message du client "+str(self.client.id)+"à été retransmit vers le client "+str(msg.dest))

            else :
                console_queue.put("Le message demande à être traité par le serveur")

                if msg.ty == TYPES['ASK_ID'] :
                    self.new_id()
                elif msg.ty == TYPES['RES_AL']:
                    self.send_anchor_list()

main()









