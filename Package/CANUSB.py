import ctypes
from ctypes import Structure, c_byte, c_ubyte,c_long, c_int, POINTER
from Package.constante import *

class CanMsg(Structure):
    _fields_ = (
        ("ID", c_long),
        ("TimeStamp", c_long),
        ("flags", c_ubyte),
        ("len", c_ubyte),
        ("data", c_ubyte *8)
    )


class CanError(Exception):
    pass

# Défini les fonctions de la dll.
class WindowsUSBCANInterface:

    def __init__(self, stop_flag):
        self.msg = None
        self._stop_flag = stop_flag
    # ======================================================================
    # Charger la DLL
        try:
            self._dll = ctypes.WinDLL("canusbdrv64.dll")
        except (OSError, FileNotFoundError) as err:
            print("Erreur DLL:", err)
            raise CanError

        # =============== DEFINITION DES FONCTIONS INTERFACE DLL =======================
        #
        # Fonction OPEN
        self._dll.canusb_Open.restype = c_long  # Type de retour : entier long
        # Fonction CLOSE
        self._dll.canusb_Close.argtypes = [c_long]
        # Fonction READ
        self._dll.canusb_Read.argtypes = [c_long, POINTER(CanMsg)]
        self._dll.canusb_Read.restype = c_int
        # Fonction STATUS
        self._dll.canusb_Status.restype = c_int
        self._dll.canusb_Read.restype = c_int

        self._handle = None

    # Fonction d'ouverture de l'adaptateur. Cette fonction est appelé par le bouton "OPEN".
    def open(self, bitrate=CAN_BAUD_250K, acceptance_code=CANUSB_ACCEPTANCE_CODE_ALL, acceptance_mask=CANUSB_ACCEPTANCE_MASK_ALL, flags=CANUSB_FLAG_TIMESTAMP):
        # Ouvre l'adapateur par l'instance
        self._handle = self._dll.canusb_Open(None, bitrate, acceptance_code, acceptance_mask, flags)
        if self._handle is None:
            raise CanError("Erreur ouverture canal CAN")
        else:
            return self._handle     # Retourne le handle dont on a besoin pour savoir si c'est ouvert

    # Fonction de lecture des trames du bus CAN.
    def read(self, stop_flag) -> CanMsg:       # Retourne un pointeur sur le CanMsg
        if self._handle is None:
           raise CanError("Channel not open")
        self.msg = CanMsg()     # Défini le format

        # On fait une boucle le temps qu'on n'a pas reçue le msg.
        while not stop_flag:
            if self._handle is None:    # C'est parque la boucle continue alors qu'on n'a plus de Handle.
                self._handle = 0        # Donc, on met le Handle avec un int.
            result = self._dll.canusb_Read(self._handle, ctypes.byref(self.msg))

            # On sort si le result=1. Sinon il a des valeurs négatives dont le -7 qui indtque qu'il n'a pas reçy de tramrs.
            if result == 1:
                break

        # Une fois qu'on a un message.
        return self.msg  # Retourne le CanMsg dont on aura besoin pour l'enregistrer

    # Fonction de fermeture de l'adaptateur.
    def close(self):
        if self._handle is not None:
            self._dll.canusb_Close(self._handle)
            self._handle = None

    # Fonction de lecture du status de l'adaptateur
    def status(self):
        if self._handle is not None:
            self._etat = self._dll.canusb_Status(self._handle)
            return self._etat
        
