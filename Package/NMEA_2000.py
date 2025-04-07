import math
from Package.CANUSB import CanMsg

# **********************************************************************************************************************
#       Programme d'analyse des trames du bus CAN et les transforment en NMEA 2000
# **********************************************************************************************************************

# Cette classe permet de déduire le PGN, sa source, son destinataire avec sa priorité ainsi que les octets.
class NMEA2000:
    def __init__(self):
        self._analyse0 = None
        self._analyse1 = None
        self._analyse2 = None
        self._analyse3 = None
        self._analyse4 = None
        self._analyse5 = None
        self._analyse6 = None
        self._analyse7 = None

        self._pgn1 = None
        self._pgn2 = None
        self._pgn3 = None
        self._valeurChoisieTab = None
        self._valeurChoisie2 = None
        self._valeurChoisie1 = None
        self._valeurChoisie3 = None
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
        self._source = msg.ID & 0xFF
        return self._source

    def destination(self,msg):
        if ((msg.ID & 0xFF0000) >> 16) < 240:
            self._destination = (msg.ID &  0x00FF00) >> 8
        else:
            self._destination = (msg.ID & 0xFF0000) >> 16
        return self._destination

    def priorite(self,msg):
        self._priorite = (msg.ID & 0x1C000000) >> 26
        return self._priorite

    # Renvoi un tuple contenant toutes les variables contenus dans l'ID
    def id(self,msg):
        return self.pgn(msg), self.source(msg) ,self.destination(msg),self.priorite(msg)
    # ================================== FIN DES METHODES POUR L'ID ====================================================

    # ========================== Méthodes de récupération des valeurs des octets =======================================
    def octets(self,msg):
        match self._pgn:
            case 130306:
                self._valeurChoisie1 = (msg.data[2] << 8 | msg.data[1]) * 0.01 * 1.94384449
                self._pgn1 = "Noeuds du Vent"

                self._valeurChoisie2 = (msg.data[4] << 8 | msg.data[3]) * 0.0001 * 180 / math.pi
                self._pgn2 = "Direction du vent"

                self._valeurChoisieTab = msg.data[5] & 0x07
                # self._PGN_Tab =    issu de la table

                # Pour Analyse.
                self._analyse2 = "Nds " + self._pgn1
                self._analyse1 = "Nds " + self._pgn1
                self._analyse4 = "Deg " + self._pgn2
                self._analyse3 = "Deg " + self._pgn2
                self._analyse5 = "Table: sur 3 bits"

            case 129026:
                self._valeurChoisie1 = (msg.data[3] << 8 | msg.data[2]) * 0.0001 * 180 / math.pi
                self._pgn1 = "COG"

                self._valeurChoisie2 = (msg.data[5] << 8 | msg.data[4]) * 0.01 * 1.94384449
                self._pgn2 = "SOG"

                # Pour Analyse.
                self._analyse3 = "Deg " + self._pgn1
                self._analyse2 = "Deg " + self._pgn1
                self._analyse5 = "Nds " + self._pgn2
                self._analyse4 = "Nds " + self._pgn2

            case 127250:
                self._valeurChoisie1 = (msg.data[2] << 8 | msg.data[1]) * 0.0001 * 180 / math.pi
                self._pgn1 = "Heading"

                # Pour Analyse.
                self._analyse2 = "Deg " + self._pgn1
                self._analyse1 = "Deg " + self._pgn1

                self._analyse4 = "Deg Déviation"
                self._analyse3 = "Deg Déviation"
                self._analyse6 = "Deg Variation"
                self._analyse5 = "Deg Variation"
                self._analyse7 = "Référence 2 bits"

            case 128267:
                self._valeurChoisie1 = (msg.data[4] << 24 | msg.data[3] << 16 |  msg.data[2] << 8 |  msg.data[1]   )  * 0.01
                self._pgn1 = "Profondeur"

                # Pour Analyse.
                self._analyse4 = "m " + self._pgn1
                self._analyse3 = "m " + self._pgn1
                self._analyse2 = "m " + self._pgn1
                self._analyse1 = "m " + self._pgn1
                self._analyse6 = "Sous la quille"
                self._analyse5 = "Sous la quille"

            case 130312:
                self._valeurChoisie1 = (msg.data[4] << 8 | msg.data[3])  * 0.01 - 273.15
                self._pgn1 = "Température"

                # Pour Analyse.
                self._analyse4 = "°C " + self._pgn1
                self._analyse3 = "°C " + self._pgn1
                self._analyse6 = "°C R&gler la temp."
                self._analyse5 = "°C R&gler la temp."

            case 130316:
                self._valeurChoisie1 = (msg.data[5] << 16 | msg.data[4] << 8 | msg.data[3]) * 0.01 - 273.15
                self._pgn1 = "Température étendue"

                # Pour Analyse.
                self._analyse5 = "°C " + self._pgn1
                self._analyse4 = "°C " + self._pgn1
                self._analyse3 = "°C " + self._pgn1
                self._analyse2 = "Table Temp."

            case 130310:
                self._valeurChoisie1 = (msg.data[2] << 8 | msg.data[1]) * 0.01 - 273.15
                self._pgn1 = "Température Mer"

                self._valeurChoisie2 = (msg.data[4] << 8 | msg.data[3]) * 0.01 - 273.15
                self._pgn2 = "Température de l'air"

                self._valeurChoisie3 = (msg.data[6] << 8 | msg.data[5])
                self._pgn3 = "Pression atmosphérique"

                # Pour Analyse.
                self._analyse2 = "°C " + self._pgn1
                self._analyse1 = "°C " + self._pgn1
                self._analyse4 = "°C " + self._pgn2
                self._analyse3 = "°C " + self._pgn2
                self._analyse6 = "mBar " + self._pgn3
                self._analyse5 = "mBar " + self._pgn3

            case 128259:
                self._valeurChoisie1 = (msg.data[2] << 8 | msg.data[1]) * 0.01 * 1.94384449
                self._pgn1 = "Vitesse surface"

                self._valeurChoisie2 = (msg.data[4] << 8 | msg.data[3]) * 0.01 * 1.94384449
                self._pgn2 = "Vitesse fond"

                self._valeurChoisietab = (msg.data[5] & 0x07)
                # self._pgntab =

                # Pour Analyse.
                self._analyse2 = "Nds " + self._pgn1
                self._analyse1 = "Nds " + self._pgn1
                self._analyse4 = "Nds " + self._pgn2
                self._analyse3 = "Table 3 bits"
                self._analyse5 = "Table 3 bits"

            case 127508:
                self._valeurChoisie1 = (msg.data[2] << 8 | msg.data[1]) * 0.01
                self._pgn1 = "Volts Batterie"

                self._valeurChoisie2 = (msg.data[4] << 8 | msg.data[3]) * 0.1
                self._pgn2 = "Ampères Batterie"

                self._valeurChoisie3 = (msg.data[6] << 8 | msg.data[5]) * 0.01 - 273.15
                self._pgn3 = "Température Batterie"

                # Pour Analyse.
                self._analyse2 = "Volts " + self._pgn1
                self._analyse1 = "Volts " + self._pgn1
                self._analyse4 = "Amp " + self._pgn2
                self._analyse3 = "Amp " + self._pgn2
                self._analyse6 = "°C " + self._pgn3
                self._analyse5 = "°C " + self._pgn3

            case 129025:
                self._valeurChoisie1 = (msg.data[3] << 24 | msg.data[2] << 16 | msg.data[1] << 8 | msg.data[0]) * (10**-7)
                self._pgn1 = "Lattitude"

                self._valeurChoisie2 = (msg.data[7] << 24 | msg.data[6] << 16 | msg.data[5] << 8 | msg.data[3]) * (10**-7)
                self._pgn2 = "Longitude"

                # Pour Analyse.
                self._analyse3 = "Coor " + self._pgn1
                self._analyse2 = "Coor " + self._pgn1
                self._analyse1 = "Coor " + self._pgn1
                self._analyse0 = "Coor " + self._pgn1
                self._analyse7 = "Coor " + self._pgn2
                self._analyse6 = "Coor " + self._pgn2
                self._analyse5 = "Coor " + self._pgn2
                self._analyse4 = "Coor " + self._pgn2

            case _:
                self._pgn1 = "<PGN inconnu sur cette version>"








