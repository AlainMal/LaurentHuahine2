import sys
import asyncio
import os

from qasync import QEventLoop

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit,QTableView, QDateEdit,
                             QHeaderView,QMessageBox, QAction, QFileDialog,
                             QAbstractItemView, QTreeWidget,QTreeWidgetItem)
from PyQt5.QtCore import Qt

from PyQt5 import uic
from PyQt5.QtGui import QIcon

from Package.CANUSB import  WindowsUSBCANInterface, CanError
from Package.constante import *
from Package.NMEA_2000 import *
from Package.VoirResult import *
from Package.TraitementCAN import TraitementCAN

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
        self.fenetre_status = None
        self._file_path = None
        self.setWindowIcon(QIcon("d:/alain/ps2.png"))
        self._traitement_can = TraitementCAN()

        #Chargement du formulaire.
        self._FenetreStatus = None
        self._can_interface = None
        self._handle = None
        self._status = None
        self._stop_flag = False

        self._can_interface = WindowsUSBCANInterface(self)

        # Importe l'UI fais avec le designer
        uic.loadUi('Alain.ui', self)

        # Variable pour les objets (Boutons, case à cocher, etc.),
        self._open = self.findChild(QPushButton, "cmd_open")
        self._close = self.findChild(QPushButton, "cmd_close")
        self._read = self.findChild(QPushButton, "cmd_read")
        self._file = self.findChild(QPushButton, "cmd_file")
        self._status = self.findChild(QPushButton, "cmd_status")
        self._stop = self.findChild(QPushButton, "cmd_stop")

        # Appel des méthodes des widgets.
        self._open.clicked.connect(self.on_click_open)
        self._close.clicked.connect(self.on_click_close)
        self._read.clicked.connect(self.on_click_read)
        self._file.clicked.connect(self.on_click_file)
        self._status.clicked.connect(self.on_click_status)
        self._stop.clicked.connect(self.on_click_stop)
        self.check_file.stateChanged.connect(self.on_check_file_changed)

        # Initialisent les  boutons à False'
        self._close.setEnabled(False)
        self._read.setEnabled(False)
        self._stop.setEnabled(False)

        # Initialise les boutons du menu<
        self.actionQuitter.triggered.connect(self.close_both)
        # Ouvre la fenêtre
        self.show()

    # ========================== DEBUT DES METHODES =========================================
    # Métode sur l'action sur la menu Quitter, on ferme tous.
    def close_both(self):
        print("Fermeture des fenêtres...")
        # Fermer FenetreStatus si elle est ouverte
        if self.fenetre_status is not None:
            self.fenetre_status.close()
            self.fenetre_status = None

        # Fermer la fenêtre courante
        print("Fermeture de la fenêtre principale")
        self.close()

    def on_click_open(self):
        # Appelle cette fonction de manière explicite et la fait passer sur "interface".
        self._handle = self._can_interface.open(CAN_BAUD_250K,
                                                CANUSB_ACCEPTANCE_CODE_ALL,
                                                CANUSB_ACCEPTANCE_MASK_ALL,
                                                CANUSB_FLAG_TIMESTAMP)
        print(f"Résultat de l'appel : {self._handle}")
        if self._handle:  # Si l'adaptateur est ouvert.
            print("C'est ouvert ...........")
            self._open.setEnabled(False)
            self._read.setEnabled(True)
            self._close.setEnabled(True)
        else:
            QMessageBox.information(self, "OUVERTURE DE L'ADAPTATEUR!", "Vérifiez que vous êtes bien raccordé")
        return self._handle

    def on_click_close(self):
        self._stop_flag = True
        if self._handle == 256:
            self._can_interface.close()  # Ferme l'adaptateur
            print("C'est complétemet arrêté.")
            self._open.setEnabled(True)
            self._close.setEnabled(False)
            self._read.setEnabled(False)
            self._stop.setEnabled(False)
            self._stop_flag = False

    def on_click_stop(self):
        self._stop_flag = True
        self._read.setEnabled(True)
        self._stop.setEnabled(False)
        print("C'est Arrêté ...")

    # Méthode Asynchrone du read sur dll, boucle tout le temps. c'est une coroutine.
    async def read(self):
        print("On est entré dans la boucle de lecture.")
        self._read.setEnabled(False)
        self._stop.setEnabled(True)
        # Boucle tant que `self._stop_flag` est False
        while not self._stop_flag:
            try:
                # Attendre qu'un message CAN soit lu de manière non-bloquante, c'est dû à l'await.
                msg = await self._can_interface.read(self._stop_flag)

                # Si on à la case à cocher, on enregistre.
                if msg and self.check_file.isChecked():
                    await self._traitement_can.enregistrer(msg,self._file_path)

            except Exception as e:
                # Gestion des erreurs pendant la lecture
                print(f"Erreur pendant la lecture CAN : {e}")

    # Méthode qui gére le read()
    async def main(self):
        # Attent le résulat du read, qui ne revoit rien, car elle tourne en permanence.
        await self.read()

    # Méthode sur clique, mêt le fonction "main()" asynchone en route
    def on_click_read(self):
        self._stop_flag = False
        if self._handle == 256:
            asyncio.ensure_future(self.main())

    def on_check_file_changed(self,state):
        if state == Qt.Checked and not self._file_path:
            self.check_file.setChecked(False)  # La remet décochée
            QMessageBox.information(self, "ENREGISTREMENT", "Veuillez choisir un fichier avant de l'activer.")

    # Méthode pour ouvrir un fichier
    def on_click_file(self):
        previous_file_path = self._file_path

        # Boîte de dialogue pour sélectionner un fichier ou en définir un nouveau
        selected_file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Ouvrir ou Créer un Fichier",  # Titre de la boîte de dialogue
            self._file_path if self._file_path else ""
            ,  # Dossier initial
            "Fichier texte (*.txt);;Tous les fichiers (*.*)"  # Types de fichiers filtres
        )

        if selected_file_path:
            self._file_path = selected_file_path
            # Si le fichier n'existe pas, le créer
            if not os.path.exists(self._file_path):
                with open(self._file_path, "w") as file:
                    file.write("")  # Crée un fichier vide
                print(f"Fichier créé : {self._file_path}")
                self.lab_file.setText(str(self._file_path))
            else:
                print(f"Fichier ouvert : {self._file_path}")
                self.lab_file.setText(str(self._file_path))
        else:
            self._file_path = previous_file_path
            print("Aucun fichier sélectionné.")

    # Méthode pour ouvrir la fenêtre des Status.
    def on_click_status(self):
        try:
            self._FenetreStatus = None
            if not self._FenetreStatus:
                self._status = self._can_interface.status()
                print("STATUS = " +str(self._status))
                self._FenetreStatus = FenetreStatus(self._status)

            self._FenetreStatus.show()
        except Exception as e:
            print(f"self._FenetreStatus.remplir_treeview(self._status) : {e}")
    # ========================== FIN DES METHODES =========================================


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Intégration asyncio avec PyQt5
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()

    # Intégration avec la boucle PyQt5
    with loop:
        loop.run_forever()