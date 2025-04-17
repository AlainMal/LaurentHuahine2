import math
from Package.constante import *
# **********************************************************************************************************************
#       Programme d'analyse des trames du bus CAN et les transforment en NMEA 2000
# **********************************************************************************************************************

# Cette classe permet de déduire le PGN, sa source, son destinataire avec sa priorité ainsi que les octets.
class NMEA2000:
    def __init__(self):
        print("NMEA2000 initialisé.")

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

        # Défini la mémoire
        nombre_octets = 8
        nombre_pgn = 255
        nombre_trames = 255
        valeur_defaut = 0

        # Crée une table 3D fixe remplie avec la valeur par défaut
        self.memoire = [[[valeur_defaut for _ in range(nombre_trames)]
                         for _ in range(nombre_pgn)]
                        for _ in range(nombre_octets)]

    # ========================== Méthodes de récupération des valeurs dans l'ID ========================================
    # On récupère le PGN, puis la source ensuite la detination ensuite la priorité.
    def pgn(self, id_msg):
        try:
            pf = (id_msg & 0x00FF0000) >> 16  # Extraire les bits PF (byte 2)
            ps = (id_msg & 0x0000FF00) >> 8  # Extraire les bits PS (byte 1)
            dp = (id_msg & 0x03000000) >> 24  # Extraire les bits DP (bits 24-25)

            if pf < 240:  # Si PF < 240, c'est un message point à point
                self._pgn = (dp << 16) | (pf << 8)  # Construire le PGN

            else:  # Sinon, c'est un message global (broadcast)
                self._pgn = (dp << 16) | (pf << 8) | ps

            return self._pgn
        except Exception as e:
            print(f"Erreur dans la méthode 'pgn' : {e}")
            raise

    def source(self,id_msg):
        self._source = id_msg & 0xFF
        return self._source

    def destination(self,id_msg):
        if ((id_msg & 0xFF0000) >> 16) < 240:
            self._destination = (id_msg &  0x00FF00) >> 8
        else:
            self._destination = (id_msg & 0xFF0000) >> 16

        return self._destination

    def priorite(self,id_msg):
        self._priorite = (id_msg & 0x1C000000) >> 26
        return self._priorite

    # Renvoi un tuple contenant toutes les variables contenus dans l'id
    def id(self,id_msg):
        return self.pgn(id_msg), self.source(id_msg) ,self.destination(id_msg),self.priorite(id_msg)
    # ================================== FIN DES METHODES POUR L'ID ====================================================

    # ================================= Méthodes de gestion de la mémoire ==============================================
    def set_memoire(self, numero_d_octet, numero_pgn, numero_de_trame, valeur):
        self.memoire[numero_d_octet][numero_pgn][numero_de_trame] = valeur

    def get_memoire(self, numero_d_octet, numero_pgn, numero_de_trame):
        return self.memoire[numero_d_octet][numero_pgn][numero_de_trame]

    # ======================================== Fin des mémoires ========================================================


    # ========================== Méthodes de récupération des valeurs des octets =======================================
    def octets(self,pgn,datas):
        print("Est bien entré dans octets.")
        self._pgn1 = None
        self._pgn2 = None
        self._pgn3 = None
        self._valeurChoisieTab = None
        self._valeurChoisie2 = None
        self._valeurChoisie1 = None
        self._valeurChoisie3 = None
        match pgn:
            case 130306:
                self._valeurChoisie1 = "{:.2f}".format((datas[2] << 8 | datas[1]) * 0.01 * 1.94384449)
                self._pgn1 = "Noeuds du Vent"

                self._valeurChoisie2 = "{:.2f}".format((datas[4] << 8 | datas[3]) * 0.0001 * 180 / math.pi)
                self._pgn2 = "Direction du vent"

                self._valeurChoisieTab = datas[5] & 0x07
                # self._PGN_Tab =    issu de la table

                # Pour Analyse.
                self._analyse2 = "Nds " + self._pgn1
                self._analyse1 = "Nds " + self._pgn1
                self._analyse4 = "Deg " + self._pgn2
                self._analyse3 = "Deg " + self._pgn2
                self._analyse5 = "Table: sur 3 bits"

            case 129026:
                self._valeurChoisie1 = "{:.2f}".format((datas[3] << 8 | datas[2]) * 0.0001 * 180 / math.pi)
                self._pgn1 = "COG"

                self._valeurChoisie2 = "{:.2f}".format((datas[5] << 8 | datas[4]) * 0.01 * 1.94384449)
                self._pgn2 = "SOG"

                # Pour Analyse.
                self._analyse3 = "Deg " + self._pgn1
                self._analyse2 = "Deg " + self._pgn1
                self._analyse5 = "Nds " + self._pgn2
                self._analyse4 = "Nds " + self._pgn2

            case 127250:
                self._valeurChoisie1 = "{:.2f}".format((datas[2] << 8 | datas[1]) * 0.0001 * 180 / math.pi)
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
                self._valeurChoisie1 = "{:.2f}".format((datas[4] << 24 | datas[3] << 16 |  datas[2] << 8 |  datas[1]   )  * 0.01)
                self._pgn1 = "Profondeur"

                # Pour Analyse.
                self._analyse4 = "m " + self._pgn1
                self._analyse3 = "m " + self._pgn1
                self._analyse2 = "m " + self._pgn1
                self._analyse1 = "m " + self._pgn1
                self._analyse6 = "Sous la quille"
                self._analyse5 = "Sous la quille"

            case 130312:
                self._valeurChoisie1 = "{:.2f}".format((datas[4] << 8 | datas[3])  * 0.01 - 273.15)
                self._pgn1 = "Température"

                # Pour Analyse.
                self._analyse4 = "°C " + self._pgn1
                self._analyse3 = "°C " + self._pgn1
                self._analyse6 = "°C R&gler la temp."
                self._analyse5 = "°C R&gler la temp."

            case 130316:
                self._valeurChoisie1 = "{:.2f}".format((datas[5] << 16 | datas[4] << 8 | datas[3]) * 0.01 - 273.15)
                self._pgn1 = "Température étendue"

                # Pour Analyse.
                self._analyse5 = "°C " + self._pgn1
                self._analyse4 = "°C " + self._pgn1
                self._analyse3 = "°C " + self._pgn1
                self._analyse2 = "Table Temp."

            case 130310:
                self._valeurChoisie1 = "{:.2f}".format((datas[2] << 8 | datas[1]) * 0.01 - 273.15)
                self._pgn1 = "Température Mer"

                self._valeurChoisie2 = "{:.2f}".format((datas[4] << 8 | datas[3]) * 0.01 - 273.15)
                self._pgn2 = "Température de l'air"

                self._valeurChoisie3 = "{:.2f}".format((datas[6] << 8 | datas[5]))
                self._pgn3 = "Pression atmosphérique"

                # Pour Analyse.
                self._analyse2 = "°C " + self._pgn1
                self._analyse1 = "°C " + self._pgn1
                self._analyse4 = "°C " + self._pgn2
                self._analyse3 = "°C " + self._pgn2
                self._analyse6 = "mBar " + self._pgn3
                self._analyse5 = "mBar " + self._pgn3

            case 128259:
                self._valeurChoisie1 = "{:.2f}".format((datas[2] << 8 | datas[1]) * 0.01 * 1.94384449)
                self._pgn1 = "Vitesse surface"

                self._valeurChoisie2 = "{:.2f}".format((datas[4] << 8 | datas[3]) * 0.01 * 1.94384449)
                self._pgn2 = "Vitesse fond"

                self._valeurChoisieTab = (datas[5] & 0x07)
                # self._pgntab =

                # Pour Analyse.
                self._analyse2 = "Nds " + self._pgn1
                self._analyse1 = "Nds " + self._pgn1
                self._analyse4 = "Nds " + self._pgn2
                self._analyse3 = "Table 3 bits"
                self._analyse5 = "Table 3 bits"

            case 127508:
                self._valeurChoisie1 = "{:.2f}".format((datas[2] << 8 | datas[1]) * 0.01)
                self._pgn1 = "Volts Batterie"

                self._valeurChoisie2 = "{:.2f}".format((datas[4] << 8 | datas[3]) * 0.1)
                self._pgn2 = "Ampères Batterie"

                self._valeurChoisie3 = "{:.2f}".format((datas[6] << 8 | datas[5]) * 0.01 - 273.15)
                self._pgn3 = "Température Batterie"

                # Pour Analyse.
                self._analyse2 = "Volts " + self._pgn1
                self._analyse1 = "Volts " + self._pgn1
                self._analyse4 = "Amp " + self._pgn2
                self._analyse3 = "Amp " + self._pgn2
                self._analyse6 = "°C " + self._pgn3
                self._analyse5 = "°C " + self._pgn3

            case 129025:
                self._valeurChoisie1 = "{:.6f}".format((datas[3] << 24 | datas[2] << 16 | datas[1] << 8 | datas[0]) * (10**-7))
                self._pgn1 = "Lattitude"

                self._valeurChoisie2 = "{:.6f}".format((datas[7] << 24 | datas[6] << 16 | datas[5] << 8 | datas[3]) * (10**-7))
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

            case 129038:
                self._valeurChoisie1 = (datas[0] & 0x1F)
                self._pgn1 = "AIS Posittion Class A"

                if self._valeurChoisie1 == 0:
                    self._valeurChoisie2 = datas[6] << 24 | datas[5] << 16 | datas[4] << 8 | datas[3]
                    self._pgn2 = "MMSI"
                    self.set_memoire(MEMOIRE_PGN_a7,PGN_129038,self._valeurChoisie1 + 1,datas[7])

                elif self._valeurChoisie1 == 1:
                    self._valeurChoisie2 = (datas[3] << 24 | datas[2] << 16 | datas[1] << 8
                                            | self.get_memoire(MEMOIRE_PGN_a7,PGN_129038,self._valeurChoisie1)) * (10**-7)
                    self._pgn2 = "AIS_A Longitude"

                    self._valeurChoisie3 = (datas[7] << 24 | datas[6] << 16 | datas[5] << 8 | datas[4] ) * (10**-7)
                    self._pgn3 = "AIS_A Latitude"

                elif self._valeurChoisie1 == 2:
                    self._valeurChoisie2 = "{:.2f}".format((datas[3] << 8 | datas[2]) * 0.0001 * 180 / math.pi)
                    self._pgn2 = "AIS_A COG"

                    self._valeurChoisie3 = "{:.2f}".format((datas[5] << 8 | datas[4]) * 0.01 * 1.94384449)
                    self._pgn3 = "AIS_A SOG"

                elif self._valeurChoisie1 == 3:
                    self._valeurChoisie2 = "{:.2f}".format((datas[3] << 8 | datas[2]) * 0.0001 * 180 / math.pi)
                    self._pgn2 = "AIS_A Heading"


            case _:
                self._pgn1 = "<PGN inconnu sur cette version>"

        # Retoune le tuple qui ne comprend pas les analyses pour l'instant.
        return (self._pgn1, self._pgn2, self._pgn3, self._valeurChoisie1,
                self._valeurChoisie2, self._valeurChoisie3, self._valeurChoisieTab)

