import tkinter as tk
from tkinter import Checkbutton, BooleanVar,ttk, filedialog
from threading import Thread
from Package.CANUSB import CanMsg, WindowsUSBCANInterface, CanError


class CANUSBReader(Thread):

    def __init__(self, interface, update_callback, file: str):
        self._interface = interface
        self._output_fd = None
        self._stop_flag = False
        self._update_callback = update_callback
        if file is not None:
            self.open_file(file)

    def stop(self):
        self._stop_flag = True

    def start(self):
        self._interface.open()
        super().start()

    def open_file(self, file):
        try:
            self._output_fd = open(file, "a")  # Créer le nouveau fichier
        except IOError as err:
            print(f"Erreur sur fichier {file}: {err}")

    def close_file(self):
        if self._output_fd is not None:
            self._output_fd.close()
            self._output_fd = None

    def run(self):
        count = 0
        while not self._stop_flag:
            try:
                msg = self._interface.read()
                if self._output_fd is not None:
                    self._output_fd.write(f"{msg.TimeStamp} {msg.Id:08X} {msg.data.hex(" ")}\n")
                if self._update_callback is not None:
                    self._update_callback(count, msg)
                count += 1
            except CanError as err:
                print("Erreur CAN", err)
                break
            except IOError as err:
                print("Erreur fichier", err)
            except Exception as err:  # catch all => à enlever
                print("Exception:", err)
                break

        self.close_file()
        self._interface.close()


class MainWindow:

    # Fonction de creation de la fenêtre principale
    def __init__(self):
        self._root = tk.Tk()
        self._root.title("LECTURE DES TRAMES EN TEMPS REEL")
        self._root.geometry("600x386")

        frame = tk.Frame(self._root)
        frame.place(x=50, y=100)
        self._can_interface = None
        self._reader = None
        self.fichier_chemin = None
        # créé l'interface avec le CAN
        try:
            self._can_interface = WindowsUSBCANInterface()
        except CanError:
            raise

        # =============== ALJOUT DES CONTROLES SUR LA FENETRE ===============================

        # Ajout d'un bouton READ et défini sa taille puis défini sont emplacement
        self.button_read = tk.Button(self._root, text="Read", width=10, height=1, command=self.on_read_click)
        self.button_read.place(x=10, y=80)

        button_stop = tk.Button(self._root, text="Arrêter", width=10, height=1, command=self.on_stop_click)
        button_stop.pack()
        button_stop.place(x=200, y=80)

        # Ajput d'une CheckBox
        self.check_enr = BooleanVar()
        check_enregistre = tk.Checkbutton(self._root, text="Enregistrer", variable=self.check_enr, command=self.on_checkbox_change)
        check_enregistre.place(x=100, y=80)  # Coordonnées précises en pixels

        # Ajout un TreeView avec 3 colonnes
        self.tree = ttk.Treeview(self._root, columns=("ID", "Length", "Data"), show="headings", height=18)
        # Positionner le Treeview et la Scrollbar
        self.tree.place(x=330, y=0)

        # Ajout des en-têtes des colonnes
        self.tree.heading("ID", text="ID")
        self.tree.heading("Length", text="Len")
        self.tree.heading("Data", text="Data")

        # Ajuster la taille des colonnes
        self.tree.column("ID", width=70)
        self.tree.column("Length", width=30)
        self.tree.column("Data", width=150)

        # Ajout d'une verticale scrollbar sur la fenêtre
        scrollbar = ttk.Scrollbar(self._root, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Ajouter un label
        self.label = tk.Label(self._root, text="Affichage du nombre de trames", width=40, anchor='w')
        self.label.place(x=5, y=10)

        # ====================== FIN DES CONTROLES ======================================

    def open(self):
        self._root.mainloop()

    # ========== FONCTIONS D'ACTIVATION ET DESACTIVATION DES BOUTONS ==========

    def disable_button_read(self):
        self.button_read['state'] = 'disabled'  # Désactive le bouton

    def enable_button_read(self):
        self.button_read['state'] = 'normal'  # Active le bouton
    # =========================================================================

    # =================== FONCTIONS DES CONTROLES SUR LA FENETRE ======================

    def on_stop_click(self):
        # Met fin à la boucle
        if self._reader is not None:
            self._reader.stop()
            self._reader.join()
            self._reader = None
        self.enable_button_read()

    def on_read_click(self):    # Lit en temps réel
        print("Bouton cliqué ! Voici votre programme de lecture.")

        self.disable_button_read()   # Desactive le boutpn READ
        # Appelle la fonction de lecture en temps réel
        self._reader = CANUSBReader(self._can_interface, self.update_read, self.fichier_chemin)
        self._reader.start()

    def update_read(self, compteur, msg):
        self.label.config(text=f"Compteur : {compteur}")
        self._root.update()

    def on_checkbox_change(self):
        if self.check_enr.get():  # Si la case est cochée
            print("Checkbox cochée - Enregistrement activé")
            # Pour récupérer le chemin et créer un nouveau fichier
            self.choix_fichier()

        else:  # Si la case est décochée
            self.fichier_chemin = None
            print("Checkbox décochée - Enregistrement désactivé")

    def on_close_click(self):
        self.on_stop_click()         # Arrête le boucle
        self._can_interface.close()    # Ferme l'adaptateur
        self.enable_button_read()    # Active le bouron d'ouverture
        result = False

    def choix_fichier(self):
        # Ouvrir une boîte de dialogue pour sélectionner un fichier
        self.fichier_chemin = filedialog.asksaveasfilename(
            title="Choisissez le fichier à enregistrer",
            filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")),
            defaultextension=".txt"
        )


    # ==================================================================================



# Lance le Thread
if __name__ == "__main__":
    main_window = MainWindow()
    main_window.open()

# =================================================================================

