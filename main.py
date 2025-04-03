import tkinter as tk
import subprocess
from tkinter import Checkbutton, BooleanVar, ttk, filedialog, messagebox
from threading import Thread
from Package.CANUSB import CanMsg, WindowsUSBCANInterface, CanError
from Package.constante import *

# *************************** CLASSE D'ENREGISTREMENT ******************************************************************
# ***********************************************************
# Classe pour ouvrir un fichier prêt pour l'enregistrement.
# ***********************************************************
class CANUSBReader(Thread):

    def __init__(self, interface, update_callback, file):
        super().__init__()
        self.msg = CanMsg()
        self._datas = ""
        self._interface = interface
        self._output_fd = None
        self._stop_flag = False
        self._update_callback = update_callback


        if file is not None:
            self.open_file(file)


    # Arreter la boucle du Read.
    def stop(self):
        self._stop_flag = True

    # Ouvrir le Thread.
    def start(self):  # C'est une fonction du Thread
        print("Lance la Thread")
        # Lance un Thread.
        super().start()

    # Ouvrir le fichier
    def open_file(self, file):
        try:
            self._output_fd = open(file, "w")  # ouvre un fichier en ajout.
        except IOError as err:
            print(f"Erreur sur fichier {file}: {err}")

    # Fermer le fichier
    def close_file(self):
        if self._output_fd is not None:
            self._output_fd.close()
            self._output_fd = None

    # Sûr en cours sur le Thread. C'est une methode particulière liée au Thread @.
    def run(self):
        count = 0
        while not self._stop_flag:  # Tant qu'on n'arrête pas ça tourne.
            try:
                if self._stop_flag:
                    self.stop()

                # Voir la boucle dans la class WindowsUSBCANInterface dans CANUSB.
                self.msg = self._interface.read(self._stop_flag)  # Lit une trame, quand il y a en une, donc, on attend.
                # print("ca boucle" + str(self.msg.ID))

                # Si on a le fichier ouvert. On enregistre quand il y a un msg.
                if self._output_fd is not None:
                    self._datas=""
                    # On défini les octets dans _datas.
                    for i in range(self.msg.len):
                        # On commence par un espace, car ça fini par le dernier octet.
                        self._datas += " " + format(self.msg.data[i], "02X") # hex(self.msg.data[i])

                    # On ne met pas d'espace entre len et datas, voir self._datas ci-dessus.
                    self._output_fd.write(f"{self.msg.TimeStamp} {self.msg.ID:08X} {self.msg.len:08X}{self._datas}\n")

                # Si on a le thread en cours, On renvoie la valeur du count
                if self._update_callback is not None:
                    self._update_callback(count, self.msg)
                count += 1  # Compte le nombre de trames.
            except CanError as err:
                print("Erreur CAN", err)
                break
            except IOError as err:
                print("Erreur fichier", err)
            except Exception as err:  # catch all => à enlever
                print("Exception:", err)
                break

        # Sinon on ferme le fichier et on ferme l'interface
        self.close_file()
        self._interface.close()
# ******************************** FIN DE LA CLASS ENREGISTREMENT ******************************************************

# ************************************ FENETRE DU STATUS ***************************************************************
class FenetreStatus:
    def __init__(self, status):
        self._status = status
        self._treeview = None

        self._fenetre_status = tk.Tk()  # Création de la fenêtre
        self._fenetre_status.title("Etats")
        self._fenetre_status.geometry("230x205")

        # Créer un Treeview
        self._colonnes = ("Colonne 1", "Colonne 2")
        self._treeview = ttk.Treeview(self._fenetre_status, columns=self._colonnes, show="headings")

        # Définir les en-têtes des colonnes
        self._treeview.heading("Colonne 1", text="Etat")
        self._treeview.heading("Colonne 2", text="")

        # Définir les largeurs des colonnes
        self._treeview.column("Colonne 1", width=150)
        self._treeview.column("Colonne 2", width=20)

        # Afficher le Treeview
        self._treeview.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        print("TreeView Installé")

    def remplir_treeview(self, status):
        # Liste des différents défauts
        status_data = (
            ("Pas de défaut", "CANSTATUS_NO_ERROR"),
            ("Buffer de réception plein", "CANSTATUS_RECEIVE_FIFO_FULL"),
            ("Buffer de transmission plein", "CANSTATUS_TRANSMIT_FIFO_FULL"),
            ( "Avertissement erreur", "CANSTATUS_ERROR_WARNING"),
            ("Surcharge des Données", "CANSTATUS_DATA_OVERRUN"),
            ("Erreur passive", "CANSTATUS_ERROR_PASSIVE"),
            ("Défaut d'arbitrage", "CANSTATUS_ARBITRATION_LOST"),
            ("Erreur sur le bus", "CANSTATUS_BUS_ERROR")
        )

        # Parcourir les données et insérer dans le TreeView
        for index, element in enumerate(status_data):
            designation = element[0]
            colonne_2 = "X" if (self._status == 0 and index == 0) else ""

            # Insérer dans le TreeView
            if self._treeview:
                self._treeview.insert("", tk.END, values=(designation, colonne_2))
            else:
                print("TreeView non initialisé.")
# *************************************** FIN DE LA FENETRE STATUS *****************************************************

# *********************************** FENETRE PRINCIPALES **************************************************************
class MainWindow:

    # Fonction de creation de la fenêtre principale
    lab_fic = None

    def __init__(self):
        self._root = tk.Tk()
        self._root.title("LECTURE DES TRAMES EN TEMPS REEL")
        self._root.geometry("600x386")

        frame = tk.Frame(self._root)
        frame.place(x=50, y=100)

        self._can_interface = None
        self._reader = None
        self.fichier_chemin = None
        self._handle = None

        self._FenetreStatus = None
        self._status = None

        # créé l'interface avec le CAN
        try:
            self._can_interface = WindowsUSBCANInterface(self)
        except CanError:
            raise

        # ====================== ALJOUT DES CONTROLES SUR LA FENETRE ===============================
        # Ajout d'un bouton OPEN et défini sa taille puis défini son emplacement
        self.button_open = tk.Button(self._root, text="Open", width=10, height=1, command=self.on_open_click)
        # button.pack(pady=20)
        self.button_open.place(x=10, y=40)

        # Ajout d'un bouton READ et défini sa taille puis défini son emplacement
        self.button_read = tk.Button(self._root, text="Read", width=10, height=1,state='disabled', command=self.on_read_click)
        self.button_read.place(x=10, y=80)

        # Ajout d'un bouton CLOSE et défini sa taille puis défini son emplacement
        self.button_close = tk.Button(self._root, text="Close", width=10, height=1, state='disabled',
                                      command=self.on_close_click)
        self.button_close.place(x=100, y=40)

        # Ajouter un bouton pour ouvrir la fenêtre des états
        self.button_status = tk.Button(self._root, text="États", width=10, height=1, command=self.on_status_click)
        self.button_status.place(x=10, y=120)

        # Ajouter un bouton pour afficher le fichier .txt.
        self.button_fichier = tk.Button(self._root, text="..", width=2, height=1, command=self.on_fichier_click)
        self.button_fichier.place(x=10, y=160)

        # Ajouter un bouton pour afficher le fichier .txt.
        self.button_stop = tk.Button(self._root, text="Arrêter ..", width=10, height=1,state='disabled', command=self.on_stop_click)
        self.button_stop.place(x=200, y=80)

        # Ajput d'une CheckBox
        self.check_enr = BooleanVar()
        check_enregistre = tk.Checkbutton(self._root, text="Enregistrer", variable=self.check_enr,
                                          command=self.on_checkbox_change)
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

        # Ajouter un label qui affiche le nombre de scrutations
        self.label = tk.Label(self._root, text="Affichage du nombre de trames reçues ", width=40, anchor='w')
        self.label.place(x=5, y=10)

        # Ajouter un label qui affiche le fichier en cours
        self.lab_fic = tk.Label(self._root, text="Fichier en cours", width=40, anchor='w')
        self.lab_fic.place(x=40, y=160)

        # ====================== FIN DES CONTROLES ======================================

    # ========== FONCTIONS D'ACTIVATION ET DESACTIVATION DES BOUTONS ==========
    def disable_button_open(self):
        self.button_open['state'] = 'disabled'  # Désactive le bouton

    def enable_button_open(self):
        self.button_open['state'] = 'normal'  # Active le bouton

    def disable_button_read(self):
        self.button_read['state'] = 'disabled'  # Désactive le bouton

    def enable_button_read(self):
        self.button_read['state'] = 'normal'  # Active le bouton

    def disable_button_close(self):
        self.button_close['state'] = 'disabled'  # Désactive le bouton

    def enable_button_close(self):
        self.button_close['state'] = 'normal'  # Active le bouton

    def disable_button_stop(self):
        self.button_stop['state'] = 'disabled'  # Désactive le bouton

    def enable_button_stop(self):
        self.button_stop['state'] = 'normal'  # Active le bouton
    # ======================= FIN D'ACTUALISATION DES BOUTONS =========================

    # =================== FONCTIONS DES CONTROLES SUR LA FENETRE ======================
    # Fonction sur OPEN click
    def on_open_click(self):
        print("Bouton cliqué ! Voici un programme d'ouverture.")

        # Exécution de la fonction OPEN
        self._can_interface = WindowsUSBCANInterface(self)

        # Appelle cette fonction de manière explicite et la fait passer sur "interface".
        self._handle = self._can_interface.open(CAN_BAUD_250K, CANUSB_ACCEPTANCE_MASK_ALL, CANUSB_ACCEPTANCE_MASK_ALL,
                                                CANUSB_FLAG_TIMESTAMP)

        print(f"Résultat de l'appel : {self._handle}")

        if self._handle:  # Si c'est l'adaptateur est ouvert.
            self.disable_button_open()  # Met le bouton d'ouverture en disabled
            self.enable_button_close()
            self.enable_button_read()
            print("C'est ouvert ...........")
        else:
            print("PAS BON !!!")
            messagebox.showinfo("OUVERTURE DE L'ADAPTATEUR", "Vérifiez que vous êtes bien raccordé")

    def on_close_click(self):
        if self._handle is not None:
            self._can_interface.close()  # Ferme l'adaptateur

            self.enable_button_open()  # Active le bouton d'ouverture
            self.disable_button_close()
            self.disable_button_read()
            self.disable_button_stop()

        if self._reader is not None:
            self._reader.stop()  # Arrête la lecture
            print("Le read est arrêté")
            self._reader = None

    def on_read_click(self):  # Lit en temps réel
        print("Bouton cliqué ! Voici votre programme de lecture.")
        if self._handle:
            self.disable_button_read()  # Desactive le bouton READ
            # Appelle la fonction de lecture en temps réel
            self._reader = CANUSBReader(self._can_interface, self.update_read, self.fichier_chemin)

            # Lance le Theard.
            self._reader.start()
            self.enable_button_stop()

    # Fonction en callback. Appelé par CANUSBReader
    def update_read(self, compteur, msg):
        self.label.config(text=f"Compteur : {compteur}")  # Affiche le nombre de trames reçues du Thread.
        self._root.update()

    def on_stop_click(self):
        if self._reader is not None:
            self._reader.stop()  # Arrête la lecture
            print("Le read est arrêté")
            self._reader = None
            self.enable_button_read()
            self.disable_button_stop()

    def on_status_click(self):
        try:
            self._FenetreStatus = None
            if not self._FenetreStatus:
                self._status = self._can_interface.status()
                self._FenetreStatus = FenetreStatus(self._status)

            print(f"Remplir TreeView avec le statut: {self._status}")
            self._FenetreStatus.remplir_treeview(self._status)  # Mettre à jour la TreeView
        except Exception as e:
            print(f"Errself._FenetreStatus.remplir_treeview(self._status)eur : {e}")

    def choix_fichier(self):
        if self.fichier_chemin != "":
            print("Fichier :" + str(self.fichier_chemin))
            # Incrit le fichier sur l'écran.
            self.lab_fic.config(text=f"Fichier : {self.fichier_chemin}")
        else:
            self.check_enr.set(False)
            self.fichier_chemin = None

    def on_checkbox_change(self):
        if self.check_enr.get():  # Si la case est cochée
            print("Checkbox cochée - Enregistrement activé")
            # Pour récupérer le chemin et créer un nouveau fichier
            self.choix_fichier()
        else:
            # self.fichier_chemin = None
            print("Checkbox décochée - Enregistrement désactivé")

    def on_fichier_click(self):
        try:
            if self.fichier_chemin is not None:
                # Afficher la boîte de dialogue
                # reponse = messagebox.askyesno("OUVRIR UN FICHIER", "Voulez-vous examiner le fichier ?,\nSinon en créer un autre")
                reponse = messagebox.askyesnocancel("OUVRIR UN FICHIER", "Voulez-vous examiner le fichier ?,\nSinon en créer un autre")
                # Gérer la réponse
                if reponse is True:
                    # Affiche le notebloc
                    subprocess.Popen(["notepad", self.fichier_chemin])
                elif reponse is False:
                    print("L'utilisateur a choisi de créer un autre fichier.")
                    # Ouvrir une boîte de dialogue pour sélectionner un fichier
                    self.fichier_chemin = filedialog.asksaveasfilename(
                        title="Choisissez le fichier à enregistrer",
                        filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")),
                        defaultextension=".txt")
                    if self.fichier_chemin != "":
                        print("Fichier :" + str(self.fichier_chemin))
                        # Incrit le fichier sur l'écran.
                        self.lab_fic.config(text=f"Fichier : {self.fichier_chemin}")
            else:
                # Ouvrir une boîte de dialogue pour sélectionner un fichier
                self.fichier_chemin = filedialog.asksaveasfilename(
                    title="Choisissez le fichier à enregistrer",
                    filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")),
                    defaultextension=".txt")
                if self.fichier_chemin == "":
                    self.fichier_chemin= None  # il y a une différence ici
                else:
                    print("Fichier :" + str(self.fichier_chemin))
                    # Incrit le fichier sur l'écran.
                    self.lab_fic.config(text=f"Fichier : {self.fichier_chemin}")
        except Exception as e:
            print(f" : {e}")
    # =================== FIN DES FONCTIONS ======================

    # **************************************** FIN DE LA CLASS MainWondow *********************************************

    # Cette fonction s'éxécute sur le lancement qui est défini ci aprés, suit le principe des déclarations.
    def open(self):
        self._root.mainloop()


# Lance la Mainwindow
if __name__ == "__main__":
    main_window = MainWindow()
    main_window.open()
# ============================================  FIN DU PROGRAMME =======================================================
