from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex

class TraitementCAN:
    def __init__(self):
          pass

    @staticmethod
    async def enregistrer(msg, file_path, coche,main_window):
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
            if msg:
                trame_list = [(f"{msg.ID:08X}", f"{msg.len} {datas}")]
                main_window.affiche_trame(trame_list)

# Cette classe sert de modèle à la table incluse dans MainWindow()
class TableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.data_table = []    # Modéle de data_table sous forme d'une liste

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
    def addTrame(self, donnees):
        debut = len(self.data_table)
        fin = debut + len(donnees) - 1

        # Notifier le modèle pour commencer l'insertion
        self.beginInsertRows(QModelIndex(), debut, fin)

        # Ajouter les données à la liste principale
        self.data_table.extend(donnees)

        # Terminer l'insertion
        self.endInsertRows()

