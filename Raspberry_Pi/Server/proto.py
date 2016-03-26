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

    def __init__(self,dest=None,ty=None,msg=None,string=None):
        global TYPES
        self.dest = "DEST"
        self.ty = "TYPE"
        self.msg = "MESS"
        if dest :
            self.dest = int(dest)
        if ty :
            self.ty = int(ty)
        if msg :
            self.msg = msg
        if string :
            self.dest = int(string[0])
            self.ty = int(string[1])
            self.msg = string[2:TYPES['MSG_SZ']]

    def str(self):
        tmp = (str(self.dest)+str(self.ty)+str(self.msg)).encode()
        return tmp#+ "#"*(MSG_SZ-len(tmp))

    def toString(self):
        return "Message : \nDEST : "+str(self.dest)+" TYPE : "+str(self.ty)+" MESS : "+str(self.msg)

