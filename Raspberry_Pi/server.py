import socket
import multiprocessing
from threading import *
import math
import sys
import time
import os
# Protocole, message = DEST TYPE MESS

MSG_SZ = 32
MSG_LN = 30

SET_ID = 0 # Donne son id à un noeud : MESS = id
CNF_ID = 1 # Confirme la reception de l'id : MESS = NULL
ASK_TY = 2 # Demande le type d'un noeud : MESS = id 
RES_TY = 3 # Donne son type  : MESS = A | M
ASK_AL = 4 # Demande la liste des ancres : MESS = id
RES_AL = 5 # Donne la liste des ancres : MESS = int + id*
""" Il sera peut etre mieux d'envoyer un premier message annoçant la taille de la liste, puis autant de message que d'item 
	dans la liste
 """
ASK_DT = 6 # Demande une evaluation de distance : MESS = id
RES_DT = 7 # Renvoi l'evaluation de distance : MESS = int
ASK_PS = 8 # Demande sa position à une ancre : MESS = id
RES_PS = 9 # Renvoi sa position : MESS = int+int

#Dans le cas des demande, l'id envoyé est celle de l'envoyeur pour que
#le receveur sache à qui envoyer la réponse


TY_ANCH = 0
TY_MOB = 1
TY_BOTH = 2

server_id = 0 #Le server à toujours pour id 0
anchor_list = [] #Liste des ancres connectées
mobile_list = [] #Liste des mobiles connecté
client_list = [] #Liste des thread client 
id_cnt = 1 #Compteur d'ID

server_th = None # Thread qui gère le server
console_th = None # Thread qui gère la console

def main():
	console_th = console()
	server_th = server(4242,5)

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
	def __init__(self,dest,code,msg):
		self.dest = dest
		self.type = code
		self.msg = msg

	def str(self):
		return str(bytes(dest))+str(bytes(type))+(mess).encode()



"""
@@@@@@@@@@@@@@@@@@@@@@@
@@@ CONSOLE @@@
@@@@@@@@@@@@@@@@@@@@@@@
"""

class console(Thread):

	def __init__(self):
		Thread.__init__(self)
		self.stack = []
		self.lock = False
		
	def run(self):
		while(True):
			st = input('[server]>')
			if st.lower() in ["exit","quit"]:
				quit()
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
	def __init__(self, port, maxQueue):
		Thread.__init__(self)
		self.sock = None
		self.port = port
		self.maxQueue = maxQueue

	def run(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind(('',self.port))
		self.sock.listen(self.maxQueue)
		console_th.println("Le server est en ligne\n"+getsockname())

		while(True):
			sock,info = server_socket.accept()
			console_th.println("Un nouveau client client s'est connecté : ip : "+info[0]+" port : "+info[1])
			client = client(sock,info,id_cnt)
			id_cnt+=1
			nw_client = thread_client(client)
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

	def close_connexion(self):
		client.sock.close()
		client_list.remove(self)
		if client.ty == TY_ANCH :
			anchor_list.remove(client)
		elif client.ty == TY_MOB :
			mobile_list.remove(client)
		elif client.ty == TY_BOTH :
			anchor_list.remove(client)
			mobile_list.remove(client)
		self.stop()

	def run(self):
		# 1 : on donne son id au client
		if not set_client_id() :
			console_th.println("Le client "+client.sock.getsockname()+" ne repond pas, déconnexion")
			close_connexion()

		if not ask_ty():
			console_th.println("Le client "+client.sock.getsockname()+" a repondu un code erroné, deconnexion")
			close_connexion()

		loop()


	def set_client_id(self):
		i=0
		while(i<MAX_ATTEMPS): #On vas tenter plusieurs fois de communiquer avec le client, apres quoi on fermera la sock si pas de reponse
			sock.send(messages(client.id,SET_ID,client.id).str()) # Envoi au nouveau client son id
			to_read = []
			try:
				to_read, wlist, xlist = select.select(client.sock,[], [], TIMEOUT)
			except select.error:
				pass
			else:
				msg = to_read.recv(MSG_SZ)
				if message_type(msg) == CNF_ID:
					return true

			i+=1
		return false

	def ask_ty(self):
		i=0
		while(i<MAX_ATTEMPS):
			sock.send(messages(client.id,ASK_TY,server_id).str()) # Demande son type au client
			to_read = []
			try:
				to_read, wlist, xlist = select.select(client.sock,[], [], TIMEOUT)
			except select.error:
				pass
			else:
				msg = to_read.recv(MSG_SZ)
				ty = -1 #TODO PARSER LES MESSAGE
				if ty == TY_ANCH : 
					console_th.println("Le client "+client.id+" est une ancre")
					anchor_list.append([client])
					return True;
				elif ty == TY_MOB : 
					console_th.println("Le client "+client.id+" est un mobile")
					mobile_list.append([client])
					return True
				elif ty == 2 :
					console_th.println("Le client "+client.id+" est une ancre et un mobile")
					anchor_list.append([client])
					mobile_list.append([client])
					return True
				else :
					return False;
			i+=1
		return False

	def loop(self):
		#Boucle de communication
		print("loop")



main()









