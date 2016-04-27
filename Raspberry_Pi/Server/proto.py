# Protocole, message = DEST TYPE MESS
import struct

TYPES = {}

TYPES['MSG_SZ'] = 64
TYPES['MSG_LN'] = 62 # Si ça merde c'est a cause de celui la !

TYPES['SERV_ID'] = 1

TYPES['SET_ID'] = 1 # Donne son id à un noeud : MESS = id
TYPES['CNF_ID'] = 2 # Confirme la reception de l'id : MESS = NULL
TYPES['ASK_TY'] = 3 # Demande le type d'un noeud : MESS = id
TYPES['RES_TY'] = 4 # Donne son type  : MESS = A | M
TYPES['CNF_TY'] = 5 # Confirme la reception du type
TYPES['ASK_AL'] = 6 # Demande la liste des ancres : MESS = id
TYPES['RES_AL'] = 7 # Donne la liste des ancres : MESS = int + id*
TYPES['ASK_DT'] = 8 # Demande une evaluation de distance : MESS = id
TYPES['RES_DT'] = 9 # Renvoi l'evaluation de distance : MESS = int
TYPES['ASK_PS'] = 10 # Demande sa position à une ancre : MESS = id
TYPES['RES_PS'] = 11 # Renvoi sa position : MESS = int+int
TYPES['ASK_ID'] = 12 # Redemande son id
TYPES['UNK_ID'] = 13 # Id inconnue, message non redirigé : MESS = dest
TYPES['IM_OUT'] = 14 # Annonce une sortie du réseau TODO
TYPES['RES_LG'] = 15 # Fichier de log MESS = CRT_X + CRT_Y + CRT_DT_1 + SIGN_1 + CRT_DT_2 + SIGN_2 + CRT_DT_3 + SIGN 3 + IT

#Dans le cas des demande, l'id envoyé est celle de l'envoyeur pour que
#le receveur sache à qui envoyer la réponse


TYPES['TY_ANCH'] = 1
TYPES['TY_MOB'] = 2
TYPES['TY_BOTH'] = 3

TYPES['BYTE_SZ'] = 64 #taille du message : 65 apres encode (), 81 sans : pour 32 char

TYPES['MAX'] = 150
TYPES['MIN'] = 0
TYPES['TL_MIN'] = 0.1
TYPES['TL_MAX'] = 50


def encode_float(f):
    buf = struct.pack('f', f)
    b = bytearray()

    for i in buf:
        b.append(i)


    return b

def decode_float(tab):
    buf = bytes(tab)
    res = struct.unpack('f', tab)
    return float(res[0])


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

        if not bytes and bytes !=0 :

            try :
                self.dest = dest
                self.ty = ty

                if msg or msg == 0 :
                    self.msg = msg
            except :
                pass

            self.bytes.append(self.dest)
            self.bytes.append(self.ty)

            if msg :
                if isinstance(self.msg,list):
                    for i in self.msg:
                        self.bytes.append(i)
                else :
                    self.bytes.append(msg)

        else :

            try :
                self.dest = bytes[0]
                self.ty = bytes[1]
                self.msg = bytes[2:TYPES['MSG_SZ']]
                self.bytes.append(self.dest)
                self.bytes.append(self.ty)
                for i in self.msg:
                        self.bytes.append(i)
            except :
                print("Plus de place")
                pass

        for i in range(len(self.bytes),TYPES["MSG_SZ"]):
            self.bytes.append(0)




    def str(self):
        #print(str(self.bytes))
        return self.bytes

    def toString(self):
        return "     -----\nMessage : \nDEST : "+str(self.dest)+" TYPE : "+str(self.ty)+" MESS : "+str(self.msg)+"\n     -----"

