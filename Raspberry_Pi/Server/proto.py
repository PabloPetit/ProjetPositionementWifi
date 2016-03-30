# Protocole, message = DEST TYPE MESS

TYPES = {}

TYPES['MSG_SZ'] = 32
TYPES['MSG_LN'] = 30

i = 1

TYPES['SET_ID'] = 1 # Donne son id à un noeud : MESS = id
TYPES['CNF_ID'] = 2 # Confirme la reception de l'id : MESS = NULL
TYPES['ASK_TY'] = 3 # Demande le type d'un noeud : MESS = id
TYPES['RES_TY'] = 4 # Donne son type  : MESS = A | M
TYPES['CNF_TY'] = 5 #Confirme la reception du type
TYPES['ASK_AL'] = 6 # Demande la liste des ancres : MESS = id
TYPES['RES_AL'] = 7 # Donne la liste des ancres : MESS = int + id*
TYPES['ASK_DT'] = 8 # Demande une evaluation de distance : MESS = id
TYPES['RES_DT'] = 9 # Renvoi l'evaluation de distance : MESS = int
TYPES['ASK_PS'] = 10 # Demande sa position à une ancre : MESS = id
TYPES['RES_PS'] = 11 # Renvoi sa position : MESS = int+int

TYPES['ASK_ID'] = 12#Demande une nouvelle id

#Dans le cas des demande, l'id envoyé est celle de l'envoyeur pour que
#le receveur sache à qui envoyer la réponse


TYPES['TY_ANCH'] = 1
TYPES['TY_MOB'] = 2
TYPES['TY_BOTH'] = 3

TYPES['BYTE_SZ'] = 32 #taille du message : 65 apres encode (), 81 sans : pour 32 char


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

    def __init__(self,dest = None,ty = None ,msg = None, bytes = None):
        global TYPES
        self.dest = int('255',8)
        self.ty = int('255',8)
        self.msg = bytearray(TYPES["MSG_LN"])

        self.bytes = bytearray()

        if not bytes :

            try :
                self.dest = int(str(dest),8)
                self.ty = int(str(ty),8)
                if msg or msg == 0 :
                    self.msg = msg
            except :
                pass

            self.bytes.append(self.dest)
            self.bytes.append(self.ty)
            if msg :
                self.bytes.append(self.msg)

        else :
            try :
                self.dest = bytes[0]
                self.ty = bytes[1]
                self.msg = bytes[2:TYPES['MSG_SZ']]
            except :
                print("plus de place")
                pass

        for i in range(0, TYPES['MSG_SZ']-len(self.bytes)):
            self.bytes.append(int('0',8))


    def str(self):
        #print(str(self.bytes))
        return self.bytes

    def toString(self):
        return "     -----\nMessage : \nDEST : "+str(self.dest)+" TYPE : "+str(self.ty)+" MESS : "+str(self.msg)+"\n     -----"

