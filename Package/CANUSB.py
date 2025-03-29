import ctypes
from ctypes import Structure, c_byte, c_ubyte,c_long, c_int, POINTER

# ======================================================================
# Charger la DLL
canusb = ctypes.WinDLL("canusbdrv64.dll")

class CanMsg(Structure):
    _fields_ = (
        ("ID", c_long),
        ("TimeStamp", c_long),
        ("flags", c_ubyte),
        ("len", c_ubyte),
        ("data", c_ubyte *8)
    )

# =============== DEFINITION DES FONCTIONS =======================
#
# Fonction OPEN
canusb.canusb_Open.restype = c_long  # Type de retour : entier long
canusb_Open = canusb.canusb_Open

# Fonction CLOSE
# canusb.canusb_Close.restype=c_long
canusb.canusb_Close.argtypes = [c_long]
canusb_Close = canusb.canusb_Close

# Fonction READ
canusb_Read = canusb.canusb_Read
canusb_Read.argtypes = [c_long, POINTER(CanMsg)]
canusb_Read.restype = c_int

# message=CanMsg