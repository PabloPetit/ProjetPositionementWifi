import socket
import multiprocessing
from queue import Queue
from threading import *
import math
import sys
import time
import os
import select
# Protocole, message = DEST TYPE MESS

TYPES = {}

TYPES['MSG_SZ'] = 32 
TYPES['MSG_LN'] = 30

TYPES['SET_ID'] = 0 # Donne son id à un noeud : MESS = id
TYPES['CNF_ID'] = 1 # Confirme la reception de l'id : MESS = NULL
TYPES['ASK_TY'] = 2 # Demande le type d'un noeud : MESS = id 
TYPES['RES_TY'] = 3 # Donne son type  : MESS = A | M
TYPES['ASK_AL'] = 4 # Demande la liste des ancres : MESS = id
TYPES['RES_AL'] = 5 # Donne la liste des ancres : MESS = int + id*
""" Il sera peut etre mieux d'envoyer un premier message annoçant la taille de la liste, puis autant de message que d'item 
	dans la liste
 """
TYPES['ASK_DT'] = 6 # Demande une evaluation de distance : MESS = id
TYPES['RES_DT'] = 7 # Renvoi l'evaluation de distance : MESS = int
TYPES['ASK_PS'] = 8 # Demande sa position à une ancre : MESS = id
TYPES['RES_PS'] = 9 # Renvoi sa position : MESS = int+int

#Dans le cas des demande, l'id envoyé est celle de l'envoyeur pour que
#le receveur sache à qui envoyer la réponse


TYPES['TY_ANCH'] = 0
TYPES['TY_MOB'] = 1
TYPES['TY_BOTH'] = 2

server_id = 0 #Le server à toujours pour id 0
anchor_list = [] #Liste des ancres connectées
mobile_list = [] #Liste des mobiles connecté
client_list = [] #Liste des thread client 
 #Compteur d'ID

server_th = None # Thread qui gère le server
console_th = None # Thread qui gère la console

console_queue = Queue()

def main():
	#console_queue = 

	console_th = console()
	server_th = server(1238,5)

	console_th.start()
	server_th.start()

"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ CLIENT - MESSAGE @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""


class client:
	def __init__(self,sock,info,id):
		self.sock = sock
		self.ip = info[0]
		self.port = info[1]
		self.id = id
		self.ty = -1

class message:
	global MSG_SZ
	def __init__(self,dest=None,ty=None,msg=None,string=None):
		self.dest = "DEST"
		self.ty = "TYPE"
		self.msg = "MESS"
		if dest : 
			self.dest = dest
		if ty :
			self.ty = ty
		if msg : 
			self.msg = msg
		if string :
			self.dest = string[0]
			self.ty = string[1]
			self.msg = string[2:32]

	def str(self):
		tmp = (str(self.dest)+str(self.ty)+str(self.msg)).encode()
		return tmp#+ "#"*(MSG_SZ-len(tmp))



"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ CONSOLE @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""

class console(Thread):

	global TYPES

	def __init__(self):
		Thread.__init__(self)
		self.stack = []
		self.lock = False
		self.queue = console_queue

	def queueService(self):
		while not self.queue.empty():
			self.println(self.queue.get())

	def run(self):
		while(True):
			#self.queueService()
			time.sleep(1)
			st = ""#input('[server]>') # Pas bon, mettre un select
			if st.lower() in ["exit","quit"]:
				self.quit()
			elif st.lower() in ["list_m"]:
				print("Liste des mobile")
			elif st.lower() in ["list_a"]:
				print("Liste des ancre")
			elif st.lower() in ["state"]:
				print("Etat global du server")
			elif st.lower() in ["reboot_server"]:
				print("Relance le server")
			elif st.lower() in ["send_msg"]:
				print("Envoi un message à un mobile")

	def quit(self):
		print("Not implemented yet")

	def println(self,st):
		#Le but de cette fonction sera de pouvoir traivailler sur un seul terminal
		#tout en evitant les print intempestif
		#Elle devra bloquer les print si l'utilisateur est entrain de saisir une commande
		#puis les imprimer quand il fini son operation
		print(st)


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
		console_queue.put("Le server est en ligne\n"+str(self.sock.getsockname()))

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
	global TYPES

	def __init__(self, client):
		Thread.__init__(self)
		self.client = client

	def close_connexion(self):
		self.client.sock.close()
		client_list.remove(self)
		if self.client.ty == TY_ANCH :
			anchor_list.remove(client)
		elif self.client.ty == TY_MOB :
			mobile_list.remove(client)
		elif self.client.ty == TY_BOTH :
			anchor_list.remove(client)
			mobile_list.remove(client)
		self.stop()

	def run(self):
		# 1 : on donne son id au client
		if not self.set_client_id() :
			console_queue.put("Le client "+str(self.client.sock.getsockname())+" ne repond pas, déconnexion")
			self.close_connexion()

		if not self.ask_ty():
			console_queue.put("Le client "+str(self.client.sock.getsockname())+" a repondu un code erroné, deconnexion")
			self.close_connexion()

		self.loop()

	def set_client_id(self):
		i=0
		while(i<self.MAX_ATTEMPS): #On vas tenter plusieurs fois de communiquer avec le client, apres quoi on fermera la sock si pas de reponse
			self.client.sock.send(message(dest=self.client.id, ty=thread_client.TYPES['SET_ID'], msg=self.client.id).str()) # Envoi au nouveau client son id
			to_read = []
			try:
				to_read, wlist, xlist = select.select([self.client.sock],[], [], thread_client.TIMEOUT)
			except select.error:
				pass
			else:
				msg = message(string=self.client.sock.recv(thread_client.TYPES['MSG_SZ']).decode())#MESSAGE
				if msg.ty == TYPES['CNF_ID']:
					return true

			i+=1
		return false

	def ask_ty(self):
		i=0
		while(i<thread_client.MAX_ATTEMPS):
			self.client.sock.send(messages(dest=self.client.id, ty=thread_client.TYPES['ASK_TY'], msg=server_id).str()) # Demande son type au client
			to_read = []
			try:
				to_read, wlist, xlist = select.select([self.client.sock],[], [], TIMEOUT)
			except select.error:
				pass
			else:
				msg = message(string=self.client.sock.recv(MSG_SZ).decode())
				ty = -1 #TODO PARSER LES MESSAGE
				if ty == thread_client.TYPES['TY_ANCH'] : 
					console_queue.put("Le client "+str(self.client.id)+" est une ancre")
					anchor_list.append([self.client])
					return True;
				elif ty == thread_client.TYPES['TY_MOB'] : 
					console_queue.put("Le client "+str(self.client.id)+" est un mobile")
					mobile_list.append([self.client])
					return True
				elif ty == 2 :
					console_queue.put("Le client "+str(self.client.id)+" est une ancre et un mobile")
					anchor_list.append([self.client])
					mobile_list.append([self.client])
					return True
				else :
					return False;
			i+=1
		return False

	def loop(self):
		#Boucle de communication
		print("loop")



main()









