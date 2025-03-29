from tkinter import Tk, filedialog

from Package.CANUSB import CanMsg


# ================== TOUTES LES FONCTIONS LIEES AU CANUSB =================================
#
# Choix du fichier pour être enregistré
def choix_fichier():
    global fichier_chemin   # Variable globale pour que ce soit utilisable partout
    # Ouvrir une boîte de dialogue pour sélectionner un fichier
    fichier_chemin = filedialog.asksaveasfilename(
        title="Choisissez le fichier à enregistrer",
        filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")),
        defaultextension=".txt"
    )
    open(fichier_chemin, "w")  # Créer le nouveau fichier
    return fichier_chemin

# Cette fonction enregistre si la case à cocher est valide et affiche le résultat sur la treeview
def enregistre(msg,tree,check_enr):
    # Vérifier si un fichier a été sélectionné
    if fichier_chemin:
        if check_enr:   # Si la case à cocher est validée
            with open(fichier_chemin,"a") as fichier:
                id_hex = f"{msg.ID:08X}"  # Hexadécimal sur 8 caractères

                # msg.len = 8 # A titre d'exemple à supprimer *********************************

                fichier.write(str(msg.TimeStamp) + " " + str(id_hex) + " " + str(msg.len) + " ")
                for i in range(msg.len):
                    fichier.write(str(f"{msg.data[i]:02X} "))
                fichier.write("\n")
                # print(f"Fichier enregistré à : {fichier_chemin}" + " " + str(msg.data))
    else:
        print("Aucun fichier sélectionné.")

    """
    # Affiche dans la treeView, à faire dans une nouvelle fonction ****************************
    data_hex = ' '.join(
    f"{byte:02X}" for byte in msg.data[:msg.len])  # Hexa sur 2 caractères par élément
    tree.insert("", "end", values=(f"{msg.ID:08X}", msg.len, data_hex))
    """
# ==========================================================================
