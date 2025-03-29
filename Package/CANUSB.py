import ctypes
from ctypes import Structure, c_byte, c_ubyte,c_long, c_int, POINTER

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


class WindowsUSBCANInterface:

    def __init__(self):
    # ======================================================================
    # Charger la DLL
        try:
            self._dll = ctypes.WinDLL("canusbdrv64.dll")
        except (OSError, FileNotFoundError) as err:
            print("Erreur DLL:", err)
            raise CanError




        # =============== DEFINITION DES FONCTIONS INTERFAC DLL=======================
        #
        # Fonction OPEN
        self._dll.canusb_Open.restype = c_long  # Type de retour : entier long
        # Fonction CLOSE
        self._dll.canusb_Close.argtypes = [c_long]
        # Fonction READ
        self._dll.canusb_Read.argtypes = [c_long, POINTER(CanMsg)]
        self._dll.canusb_Read.restype = c_int
        self._handle = None


    def open(self, bitrate=b"250", acceptance_code=0, acceptance_mask=0xFFFFFFFF, flags=1):
        """
        ouvre le canal d'accès au bus

        :return:
        rien. Exception CanError si problème
        """
        self._handle = self._dll.canusb_Open(None, bitrate, acceptance_code, acceptance_mask, flags)
        if self._handle is None:
            raise CanError("Erreur ouverture canal CAN")

    def read(self) -> CanMsg:
        if self._handle is None:
           raise CanError("Channel not open")
        msg = CanMsg()
        result = self._dll.canusb_Read(self._handle, ctypes.byref(msg))
        if result:
            return msg
        else:
            raise CanError("Erreur sur lecture CAN")

    def close(self):
        self._dll.canusb_Close(self._handle)
        self._handle = None

# message=CanMsg