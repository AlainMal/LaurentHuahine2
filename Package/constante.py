CAN_BAUD_250K = b"250"
CANUSB_ACCEPTANCE_CODE_ALL = 0x0
CANUSB_ACCEPTANCE_MASK_ALL = 0xFFFFFFFF
FLUSH_WAIT = 0x0
FLUSH_DONTWAIT = 0x1
CANUSB_FLAG_TIMESTAMP = 0x1

CANSTATUS_NO_ERROR = 0x0
CANSTATUS_RECEIVE_FIFO_FULL = 0x1
CANSTATUS_TRANSMIT_FIFO_FULL = 0x2
CANSTATUS_ERROR_WARNING = 0x4
CANSTATUS_DATA_OVERRUN = 0x8
CANSTATUS_ERROR_PASSIVE = 0x20
CANSTATUS_ARBITRATION_LOST = 0x40
CANSTATUS_BUS_ERROR = 0x80

"""
class MainWindow:
    def __init__(self):
        self._status = None
        self._FentreStatus = None

    def initialize_status(self):
        if not self._FentreStatus:
            self._status = self._can_interface.status()
            self._FentreStatus = FentreStatus(self._status)

    def on_status_click(self):
        try:
            if self._handle:
                self.initialize_status()  # Assurez-vous que FentreStatus est initialisé
                self._status = self._can_interface.status()  # Récupérer le statut actuel
                print(f"Remplir TreeView avec le statut: {self._status}")
                self._FentreStatus.remplir_treeview(self._status)  # Mettre à jour le TreeView
        except Exception as e:
            print(f"Erreur : {e}")


"""