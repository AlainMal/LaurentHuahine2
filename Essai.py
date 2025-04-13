from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

from PyQt5.uic import loadUi


class LargeTableModel(QAbstractTableModel):
    """
    Modèle optimisé pour afficher des trames (32 octets sous forme de str).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trames = []  # Stockage de trames sous forme de liste de str

    def rowCount(self, parent=None):
        return len(self.trames)  # Retourne le nombre de lignes dans la table

    def columnCount(self, parent=None):
        return 2  # Deux colonnes pour afficher les trames

    def data(self, index, role=Qt.DisplayRole):
        # Vérifie si l'index est valide
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()

            # Retourne la donnée correspondante à la colonne
            return self.trames[row][col]

        return None


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Colonne 1"  # Nom de la 1ère colonne
                elif section == 1:
                    return "Colonne 2"  # Nom de la 2ème colonne
            elif orientation == Qt.Vertical:
                return str(section)  # Numéro des lignes
        return None


    def addTrame(self, col1_value, col2_value):
        """
        Ajoute une trame dans la liste et met à jour la vue.
        """
        print(f"Ajout d'une ligne : Colonne 1 = {col1_value}, Colonne 2 = {col2_value}")


        self.beginInsertRows(self.createIndex(len(self.trames), 0), len(self.trames), len(self.trames))
        self.trames.append((col1_value, col2_value)
)
        self.endInsertRows()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Importe l'UI fais avec le designer
        loadUi('Alain.ui', self)

        # Configurer la table
        self.model = LargeTableModel()
        self.table_can.setModel(self.model)  # "table_can" vient du fichier .ui configuré dans Qt Designer
        self.configure_table()

        # Ajout des trames d'exemple
        self.add_sample_data()

    def configure_table(self):
        """
        Configure les propriétés spécifiques de `table_can`.
        """
        self.table_can.setSelectionBehavior(self.table_can.SelectRows)  # Sélection des lignes
        self.table_can.setSelectionMode(self.table_can.SingleSelection)  # Une seule ligne à la fois

    def add_sample_data(self):
        """
        Ajoute des trames d'exemple pour populater le tableau.
        """
        trames = [
            ("AB CD 12 34 56 78 9A BC", "Info complémentaire 1"),
            ("01 23 45 67 89 AB CD EF", "Info complémentaire 2"),
            ("FF EE DD CC BB AA 99 88", "Info complémentaire 3"),
        ]

        for trame in trames:
            col1, col2 = trame  # Déballage du tuple en deux variables
            self.model.addTrame(col1, col2)  # Ajoute chaque colonne


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
