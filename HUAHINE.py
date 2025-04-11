import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit,QTableView, QDateEdit,
                             QHeaderView,QMessageBox, QAction, QFileDialog, QAbstractItemView, QTreeWidget,QTreeWidgetItem)
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
from PyQt5 import uic
from PyQt5.QtGui import QIcon

from Package.CANUSB import  WindowsUSBCANInterface, CanError
from Package.constante import *
from Package.NMEA_2000 import *
from Package.VoirResult import *

# ************************************ FENETRE DU STATUS ***************************************************************
class FenetreStatus(QMainWindow):
    def __init__(self, status):
        super(FenetreStatus, self).__init__()
        self._status = status
        self.setFixedSize(290, 230)
        self.setWindowTitle("Statuts")

        # Création du QTreeWidget
        self._treewidget = QTreeWidget(self)
        self._treewidget.setColumnCount(2)
        self._treewidget.setHeaderLabels(["Désignations", "Etats"])
        self.setCentralWidget(self._treewidget)

        self._treewidget.setColumnWidth(0, 230)  # Définit la largeur de la première colonne à 200 pixels
        self._treewidget.setColumnWidth(1, 7)

        # Remplir le TreeWidget
        self.remplir_treewidget()

    # ========================== DEBUT DES METHODES STATUS =========================================
    def remplir_treewidget(self):
        # La liste des différents défauts
        status_data = (
            ("Pas de défaut", "CANSTATUS_NO_ERROR"),
            ("Buffer de réception plein", "CANSTATUS_RECEIVE_FIFO_FULL"),
            ("Buffer de transmission plein", "CANSTATUS_TRANSMIT_FIFO_FULL"),
            ("Avertissement erreur", "CANSTATUS_ERROR_WARNING"),
            ("Surcharge des Données", "CANSTATUS_DATA_OVERRUN"),
            ("Erreur passive", "CANSTATUS_ERROR_PASSIVE"),
            ("Défaut d'arbitrage", "CANSTATUS_ARBITRATION_LOST"),
            ("Erreur sur le bus", "CANSTATUS_BUS_ERROR")
        )

        # Vérifiez que le widget TreeWidget existe
        if self._treewidget:
            # Parcourir les données et insérer dans le TreeWidget
            for index, element in enumerate(status_data):
                designation = element[0]
                colonne_2 = "X" if (self._status == 0 and index == 0) else ""

                # Ajouter un élément dans le TreeWidget
                item = QTreeWidgetItem([designation, colonne_2])
                self._treewidget.addTopLevelItem(item)

            print("TREEWIDGET INSTALLE")
# *************************************** FIN DE LA FENETRE STATUS *****************************************************

# ***************************************** FENETRE PRINCIAPALE ********************************************************
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setWindowIcon(QIcon("d:/alain/ps2.png"))
        #Chargement du formulaire.
        self._reader = None
        self._FenetreStatus = None
        self._can_interface = None
        self._handle = None
        self._status = None

        self._can_interface = WindowsUSBCANInterface(self)

        # Importe l'UI fais avec le designer
        uic.loadUi('Alain.ui', self)

        # Variable pour les objets (Boutons, case à cocher, etc.),
        self._open = self.findChild(QPushButton, "cmd_open")
        self._close = self.findChild(QPushButton, "cmd_close")
        self._read = self.findChild(QPushButton, "cmd_read")
        self._file = self.findChild(QPushButton, "cmd_file")
        self._status = self.findChild(QPushButton, "cmd_status")

        # Appel des méthodes des widgets.
        self._open.clicked.connect(self.on_click_open)
        self._close.clicked.connect(self.on_click_close)
        self._read.clicked.connect(self.on_click_read)
        self._file.clicked.connect(self.on_click_file)
        self._status.clicked.connect(self.on_click_status)

        # Ouvre la fenêtre
        self.show()

    # ========================== DEBUT DES METHODES =========================================
    def on_click_open(self):
        print("Bouton cliqué ! Voici un programme d'ouverture.")
        # défini une instance de la classe

        # Appelle cette fonction de manière explicite et la fait passer sur "interface".
        self._handle = self._can_interface.open(CAN_BAUD_250K,
                                                CANUSB_ACCEPTANCE_MASK_ALL,
                                                CANUSB_ACCEPTANCE_MASK_ALL,
                                                CANUSB_FLAG_TIMESTAMP)
        print(f"Résultat de l'appel : {self._handle}")
        if self._handle:  # Si l'adaptateur est ouvert.
           print("C'est ouvert ...........")
        else:
            QMessageBox.information(self, "OUVERTURE DE L'ADAPTATEUR!", "Vérifiez que vous êtes bien raccordé")

    def on_click_close(self):
        print("Bouton 'cmd_close' cliqué !")
        if self._handle is not None:
            self._can_interface.close()  # Ferme l'adaptateur

            print("Le read est arrêté")
            self._reader = None

    def on_click_read(self):
        print("Bouton cliqué ! Voici votre programme de lecture.")
        if self._handle:
            # Appelle la fonction de lecture en temps réel. À modifier pour qu'elle se fasse en temps réel par asyncio.
            self._reader = self._can_interface.read(self._stop_flag)

    def on_click_status(self):
        try:
            self._FenetreStatus = None
            if not self._FenetreStatus:
                self._status = self._can_interface.status()
                print("STATUS = " +str(self._status))
                self._FenetreStatus = FenetreStatus(self._status)

            print(f"Remplir TreeView avec le statut: {self._status}")
            self._FenetreStatus.show()
            self._FenetreStatus.remplir_treeview()  # Mettre à jour la TreeView
        except Exception as e:
            print(f"self._FenetreStatus.remplir_treeview(self._status) : {e}")

    def on_click_file(self):
        print("Bouton 'cmd_fichier' cliqué !")
    # ========================== FIN DES METHODES =========================================

app = QApplication(sys.argv)
window = MainWindow()
app.exec_()