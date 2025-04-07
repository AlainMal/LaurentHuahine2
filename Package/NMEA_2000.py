from Package.CANUSB import CanMsg

# **********************************************************************************************************************
#       Programme d'analyse des trames du bus CAN et les transforment en NMEA 2000
# **********************************************************************************************************************

# Cette classe permet de déduire le PGN, sa source, son destinataire avec sa priorité ainsi que les octets.
class NMEA2000:
    def __init__(self):
        self._priorite = None
        self._destination = None
        self._source = None
        self._pgn = None

    # ========================== Méthodes de récupération des valeurs dans l'ID ========================================
    # On récupère le PGN
    def pgn(self,msg):
        pf = (msg.ID & 0xFF0000) >> 8
        ps = (msg.ID &  0x00FF00) >> 8
        dp = (msg.ID & 0x1000000) >> 8
        if (pf >> 8) < 240:
            self._pgn = ps or dp
        else:
            self._pgn = pf or ps or dp
        return self._pgn

    def source(self,msg):
        self._source = msg.ID and 0xFF
        return self._source

    def destination(self,msg):
        if ((msg.ID & 0xFF0000) >> 16) < 240:
            self._destination = (msg.ID and  0x00FF00) >> 8
        else:
            self._destination = (msg.ID and 0xFF0000) >> 16
        return self._destination

    def priorite(self,msg):
        self._priorite = (msg.ID and 0x1C000000) >> 26
        return self._priorite

    # Renvoi un tuple contenant toutes les variables contenus dans l'ID
    def id(self,msg):
        return self.pgn(msg), self.source(msg) ,self.destination(msg),self.priorite(msg)
    # ================================== ,FIN DES METHODES POUR L'ID ===================================================





