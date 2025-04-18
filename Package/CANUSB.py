import ctypes
import asyncio
from concurrent.futures import ThreadPoolExecutor
from ctypes import Structure, c_ubyte,c_long, c_int, POINTER
from Package.constante import *


class CanMsg(Structure):
    _fields_ = (
        ("ID", c_long),
        ("TimeStamp", c_long),
        ("flags", c_ubyte),
        ("len", c_ubyte),
        ("data", c_ubyte*8)
    )

# Défini les fonctions de la dll.
class CanError(Exception):
    pass


class WindowsUSBCANInterface:

    def __init__(self, stop_flag):
        self._etat = None
        self.msg = None
        self._stop_flag = stop_flag
        self.executor = ThreadPoolExecutor()

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

        self._handle = None

    # Fonction d'ouverture de l'adaptateur. Cette fonction est appelé par le bouton "OPEN".
    def open(self, bitrate=CAN_BAUD_250K,
             acceptance_code=CANUSB_ACCEPTANCE_CODE_ALL,
             acceptance_mask=CANUSB_ACCEPTANCE_MASK_ALL,
             flags=CANUSB_FLAG_TIMESTAMP):
        # Ouvre l'adapateur par l'instance
        self._handle = self._dll.canusb_Open(None, bitrate, acceptance_code, acceptance_mask, flags)
        if self._handle is None:
            raise CanError("Erreur ouverture canal CAN")
        else:
            return self._handle     # Retourne le handle dont on a besoin pour savoir si c'est ouvert

    # Fonction de lecture des trames du bus CAN en asychrone.
    async def read(self, stop_flag) -> CanMsg:       # Retourne un pointeur sur le CanMsg
        if self._handle is None:
           raise CanError("Channel not open")
        self.msg = CanMsg()     # Défini le format

        # Boucle pour attendre les trames CAN.
        while not stop_flag:
            if self._handle is None:
                self._handle = 0    # Marquer le handle en entier comme inactif

            result = await asyncio.get_event_loop().run_in_executor(
                            self.executor,
                            self._dll.canusb_Read,      # Appel la fonction en dll
                            self._handle,         # Récupère le _handle
                            ctypes.byref(self.msg))     # Paramètres passés par référence à la fonction native

            # Résultat du CAN : on sort si une trame a été reçue : result == 1.
            # Sinon il a des valeurs négatives qui représente différent défaut,
            # dont le -7 qui indtque qu'il n'a pas reçu de tramrs.
            if result <= -2 and result != -7:
                # On ne traite pas les défauts, mais on le signale.
                print("Défaut CAN : ", str(result))
            if result == 1:
                break

        # On attend 10ms pour éviter le blocage complet de la boucle asyncio. Peut-être supprimé ?
        # await asyncio.sleep(0.01)

        # Une fois une trame reçue, on la retourne
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
        
