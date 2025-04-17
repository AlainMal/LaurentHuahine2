import asyncio
import os
import sys

from qasync import QEventLoop
from PyQt5.QtWidgets import QPushButton, QTableView, QMessageBox, QFileDialog, QTreeWidget, QTreeWidgetItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QAbstractItemView
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from Package.CANUSB import WindowsUSBCANInterface
from Package.constante import *
from Package.TraitementCAN import TraitementCAN
from Package.NMEA_2000 import NMEA2000

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

                # Ajouter l'élément dans le TreeWidget
                item = QTreeWidgetItem([designation, colonne_2])
                self._treewidget.addTopLevelItem(item)

            print("TREEWIDGET REMPLI")
# *************************************** FIN DE LA FENETRE STATUS *****************************************************


# ********************************** CLASSE MODELE DE LA TABLE *********************************************************
# Cette classe sert de modèle à la table incluse dans MainWindow()
class TableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.data_table = []    # Modéle de data_table sous forme d'une liste

    def clear(self):
        # Supprime tous les éléments de la table de données
        self.beginResetModel()  # Notifie la vue d'une réinitialisation des données
        self.data_table = []  # Vide les données
        self.endResetModel()  # Permet à la vue de rafraîchir l'interface

    def rowCount(self, parent=None):
        return len(self.data_table)  # Retourne le nombre de lignes dans la table

    def columnCount(self, parent=None):
        return 3    # 3 colonnes

    # Cette méthode retourne le data_frame
    def data(self, index: QModelIndex, role= Qt.ItemDataRole.DisplayRole):
        if role == Qt.DisplayRole:
            return self.data_table[index.row()][index.column()]

    # Cette méthode définie trois sections avec leurs entêtes.
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "ID"  # Nom de la 1ᵉre colonne
                elif section == 1:
                    return "Len"  # Nom de la 2ème colonne
                elif section == 2:
                    return "Data"  # Nom de la 2ème colonne
            elif orientation == Qt.Vertical:
                return str(section)  # Numéro des lignes
        return None

    # Cette méthode ajoute les données à la table, voir dans la classe MainWindows.
    def addTrame(self, donnees, batch_size=1000):
        total_donnees = len(donnees)
        for i in range(0, total_donnees, batch_size):
            batch = donnees[i: i + batch_size]  # Crée un lot, de taille batch_size

            debut = len(self.data_table)
            fin = debut + len(batch) - 1

            # Notifier le modèle pour commencer l'insertion
            self.beginInsertRows(QModelIndex(), debut, fin)

            # Ajouter les données à la liste principale
            self.data_table.extend(batch)

            # Terminer l'insertion
            self.endInsertRows()
# ************************************ FIN DE LA CLASSE  TableModel ****************************************************


# ***************************************** FENETRE PRINCIAPALE ********************************************************
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self._fenetre_status = None
        self._file_path = None
        self.setWindowIcon(QIcon("d:/alain/ps2.png"))
        self._traitement_can = TraitementCAN()
        print("avant NMEA2000")
        self._nmea_2000 = NMEA2000()
        print("apres NMEA2000" + str(self._nmea_2000))

        #Chargement du formulaire.
        self._can_interface = None
        self._handle = None
        self._status = None
        self._stop_flag = False

        # Importe l'UI fais avec le designer
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        uic.loadUi('Alain.ui', self)

        self._can_interface = WindowsUSBCANInterface(self)

        # Variable pour les objets (Boutons, case à cocher, etc.)
        self._table = self.findChild(QTableView, 'table_can')
        self._open = self.findChild(QPushButton, "cmd_open")
        self._close = self.findChild(QPushButton, "cmd_close")
        self._read = self.findChild(QPushButton, "cmd_read")
        self._file = self.findChild(QPushButton, "cmd_file")
        self._status = self.findChild(QPushButton, "cmd_status")
        self._stop = self.findChild(QPushButton, "cmd_stop")
        self._voir = self.findChild(QPushButton, "cmd_voir")
        self._import = self.findChild(QPushButton, "cmd_import")

        # Appel des méthodes des widgets.
        self._open.clicked.connect(self.on_click_open)
        self._close.clicked.connect(self.on_click_close)
        self._read.clicked.connect(self.on_click_read)
        self._file.clicked.connect(self.on_click_file)
        self._status.clicked.connect(self.on_click_status)
        self._stop.clicked.connect(self.on_click_stop)
        self._voir.clicked.connect(self.on_click_voir)
        self._import.clicked.connect(self.on_click_import)
        self.check_file.stateChanged.connect(self.on_check_file_changed)
        self.table_can.clicked.connect(self.on_click_table)
        self.table_can.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_can.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.model = TableModel()
        self.table_can.setModel(self.model)
        # Connecter le signal selectionChanged
        self.table_can.selectionModel().selectionChanged.connect(self.on_selection_changed)
        # Configurer les largeurs des colonnes
        self.configurer_colonnes()

    # ========================== DEBUT DES METHODES =========================================
    def on_selection_changed(self):
        """
        Méthode appelée lorsqu'une sélection change, que ce soit via le clavier ou la souris.
        """
        indexes = self.table_can.selectionModel().selectedRows()
        if indexes:  # Vérifier s'il y a une sélection active
            self.on_click_table(indexes[0])  # Passer la première ligne sélectionnée à on_click_table

    def on_click_table(self, index: QModelIndex):
        """
        Récupère les données de la ligne sélectionnée.
        """
        model = self.table_can.model()  # Récupérer le modèle de la table
        ligne = index.row()  # Récupérer l'indice de la ligne cliquée

        # Extraire les valeurs des 3 colonnes
        col1 = model.data(model.index(ligne, 0), Qt.DisplayRole)
        # col2 = model.data(model.index(ligne, 1), Qt.DisplayRole)
        col3 = model.data(model.index(ligne, 2), Qt.DisplayRole)

        print(f"Valeur de col1: {col1} (type: {type(col1)})")
        col1= col1.strip()
        if not col1.startswith("0x"):
            col1 = f"0x{col1}"

        id_msg = int(col1, 16)
        print(f"ID de message converti : {id_msg}")
        tout_id = self._nmea_2000.id(id_msg)
        print(tout_id)

        self.lab_pgn.setText("Issu de l'ID: PGN, Source, Destination, Priorité :\n                     "
                             + str(tout_id))

        # Diffuse le résultat des octets avec leurs définitions.
        if col3:
            data = col3.split(" ")
            print("PGN = " + str(int(tout_id[0])))
            print("DATAS = " + str([int(octet,16) for octet in data]))
            try:
                octetstuple = self._nmea_2000.octets(int(tout_id[0]),[int(octet,16) for octet in data])
                print(f"Résultat octets : {octetstuple}")
                self.lab_octet.setText("PGN:" + str(tout_id[0]) + "\n" + str(octetstuple[0]) + ": " + str(octetstuple[3]) + "\n"
                                       + str(octetstuple[1]) + ": " + str(octetstuple[4]) + "\n"
                                       + str(octetstuple[2]) + ": " + str(octetstuple[5]) + "\n"
                                       + "Table : " + str(octetstuple[6]))

                print(octetstuple)
            except Exception as e:
                print(f"Erreur dans l'appel à octets : {e}")

    def on_click_voir(self):
        pass

    # Cette méthode écrit avec addTrame défini dans la classe TableModel()
    def affiche_trame(self,trame):
        self.model.addTrame(trame)

    def configurer_colonnes(self):
        self.table_can.setColumnWidth(0, 80)  # Largeur de "ID"
        self.table_can.setColumnWidth(1, 30)  # Largeur de "Len"
        self.table_can.setColumnWidth(2, 180)  # Largeur de "Data"

        # Initialisent les boutons à False'
        self._close.setEnabled(False)
        self._read.setEnabled(False)
        self._stop.setEnabled(False)

        # Initialise les boutons du menu, Quitter
        self.actionQuitter.triggered.connect(self.close_both)

        # Ouvre la fenêtre
        self.show()

    # Métode sur fermeture de la fenêtre sue événemnt
    def closeEvent(self, event):
        # Appelle la méthode `close_both` pour gérer la fermeture proprement
        self.close_both()
        # Accepte l'événement pour continuer la fermeture
        event.accept()

    # Métode sur l'action sur le menu Quitter, on ferme tous.
    def close_both(self):
        print("Fermeture des fenêtres...")
        # Fermer FenetreStatus si elle est ouverte
        if self._fenetre_status is not None:
            print("Fermeture de la fenetre_status")
            self._fenetre_status.close()
            self._fenetre_status = None

        # Fermer la fenêtre courante
        print("Fermeture de la fenêtre principale")
        self._stop_flag = True
        self.on_click_close()
        self.close()

    def on_click_open(self) -> int:
        self.setCursor(Qt.WaitCursor)

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
        self.unsetCursor()

        return self._handle

    def on_click_close(self) -> None:
        self.setCursor(Qt.WaitCursor)

        self._stop_flag = True
        if self._handle == 256:
            self._can_interface.close()  # Ferme l'adaptateur
            print("C'est complétemet arrêté.")
            self._open.setEnabled(True)
            self._close.setEnabled(False)
            self._read.setEnabled(False)
            self._stop.setEnabled(False)
            self._stop_flag = False
            self._handle = None
        self.unsetCursor()
        return None

    def on_click_stop(self):
        self._stop_flag = True
        self._read.setEnabled(True)
        self._stop.setEnabled(False)
        print("C'est Arrêté ...")

    # Méthode Asynchrone du read sur dll, boucle tout le temps et c'est une coroutine.
    async def read(self):
        print("On est entré dans la boucle de lecture.")
        n = 0
        # Boucle tant que `self._stop_flag` est False
        while not self._stop_flag :
            try:
                # Attendre qu'un message CAN soit lu de manière non-bloquante, c'est dû à l'await.
                msg = await self._can_interface.read(self._stop_flag)
                n += 1
                self.lab_trame.setText(str(n))  # Affiche le nombre de trames reçues.
                # On enregistre ***********************************************************************VVVV
                await self._traitement_can.enregistrer(msg,self._file_path,self.check_file.isChecked(),self)
                # return msg

            except Exception as e:
                # Gestion des erreurs pendant la lecture
                print(f"Erreur pendant la lecture CAN : {e}")
        print("Tache terminée")
    # Méthode qui gére le read()
    async def main(self) -> None:
        # Attent le résulat du read, qui ne revoit rien,
        # car elle tourne en permanence.
        self._read.setEnabled(False)
        self._stop.setEnabled(True)
        await self.read()

    # Méthode sur clique, mêt le fonction "main()" asynchone en route
    def on_click_read(self) -> None:
        self._stop_flag = False
        if self._handle == 256:
            asyncio.ensure_future(self.main())

    def on_check_file_changed(self,state) :
        if state == Qt.Checked and not self._file_path:
             # La remet décochée
            QMessageBox.information(self, "ENREGISTREMENT", "Veuillez choisir un fichier avant de l'activer.")
            # self._file.setfocus()
            self.check_file.setChecked(False)

            return self.check_file

    # Méthode pour ouvrir un fichier
    def on_click_file(self) -> os.path:
        self.setCursor(Qt.WaitCursor)

        __previous_file_path = self._file_path

        # Boîte de dialogue pour sélectionner un fichier ou en définir un nouveau
        selected_file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Ouvrir ou Créer un Fichier",  # Titre de la boîte de dialogue
            self._file_path if self._file_path else ""
            ,  # Dossier initial
            "Fichier texte (*.txt);;Tous les fichiers (*.*)")

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
            self._file_path = __previous_file_path
            print("Aucun fichier sélectionné.")

        self.unsetCursor()

    # Méthode pour ouvrir la fenêtre des Status.
    def on_click_status(self) :
        try:
            self._fenetre_status = None
            if not self._fenetre_status:
                self._status = self._can_interface.status()
                print("STATUS = " +str(self._status))
                self._fenetre_status = FenetreStatus(self._status)

            if not self._handle:
                QMessageBox.information(self, "STAUS", "Il n'y a pas de status,\ncar vous n'êtes pas raccordé.")
            self._fenetre_status.show()

        except Exception as e:
            print(f"self._FenetreStatus.remplir_treeview(self._status) : {e}")

    def on_click_import(self):
        if not self._file_path:
            QMessageBox.information(self,"IMPORTER LE FICHIER","Veuillez sélectionner un fichier avant d'importer")
            return None
        try:
            QMessageBox.information(self, "IMPORTER", "Vous allez importer les 3000 premières du fichier")
            # self.setCursor(Qt.WaitCursor)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.model.data_table = []

            liste_tuples = []
            with open(self._file_path, 'r', encoding='utf-8',errors='replace') as fichier:
                for i, ligne in enumerate(fichier):
                    # Supprimer les espaces inutiles
                    ligne = ligne.strip()
                    valeurs = ligne.split(' ')
                    # Convertit la liste de valeurs en tuple
                    ligne_tuple = tuple(valeurs)

                    # Ajoute le tuple à la liste
                    liste_tuples.append(ligne_tuple)
                    if i >=2999:
                        break
                    liste_modifiee = [
                        (
                            t[1],  # 2e élément d'origine
                            t[2] if len(t) > 2 else '',  # 3e élément d'origine
                            ' '.join(t[3:]) if len(t) > 3 else ''  # Reste concaténé
                        )
                        for t in liste_tuples]

                    self.affiche_trame(liste_modifiee)
                # self.unsetCursor()
        except FileNotFoundError:
            print(f"Fichier non trouvé : {self._file_path}")
            # self.unsetCursor()

        finally:
            QApplication.restoreOverrideCursor()


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