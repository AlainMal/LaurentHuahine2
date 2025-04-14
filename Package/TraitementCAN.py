from typing import Any, Coroutine

from PyQt5.QtCore import Qt, QAbstractTableModel

class TraitementCAN:
    def __init__(self):
          pass

    @staticmethod
    async def enregistrer(msg, file_path, coche):
        # print("Message CAN reçu :", msg)
        datas = ""
        # On va définir les octets dans "datas".
        for i in range(msg.len):
            # On commence par un espace, car ça fini par le dernier octet.
            datas += " " + format(msg.data[i], "02X")
            # On ne met pas d'espace entre len et datas, voir les datas ci-dessus.
            if msg and coche:
                with open(file_path, "w") as file:
                    file.write(f"{msg.TimeStamp} {msg.ID:08X} {msg.len}{datas}\n")

class TableModel(QAbstractTableModel):
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
