import tkinter as tk
from tkinter import Checkbutton, BooleanVar,ttk, filedialog
from threading import Thread
from Package.CANUSB import CanMsg, WindowsUSBCANInterface, CanError
from Package.constante import *
# *************************** CLASSE D'ENREGISTREMENT ******************************************************************
# ***********************************************************
# Classe pour ouvrir un fichier prêt pour l'enregistrement.
# Il serait mieux de metter le Thread sur la boucle de lecture
# qu'on enregistre ou PAS.
# ***********************************************************
class CANUSBReader(Thread):

    def __init__(self, interface, update_callback, file: str):
        super().__init__()
        self._interface = interface
        self._output_fd = None
        self._stop_flag = False
        self._update_callback = update_callback
        if file is not None:
            self.open_file(file)

    # Arreter la boucle du Read.
    def stop(self):
        self._stop_flag = True

    # Ouvrir l'interface.
    def start(self):    # C'est une fonction du Thread
        print("Lance la Thread")
        # Lance un Thread.
        super().start()
    
    # Ouvrir le fichier
    def open_file(self, file):
        try:
            self._output_fd = open(file, "a")  # Créer le nouveau fichier
        except IOError as err:
            print(f"Erreur sur fichier {file}: {err}")

    # Fermer le fichier
    def close_file(self):
        if self._output_fd is not None:
            self._output_fd.close()
            self._output_fd = None

    # Sûr en cours sur le Thread. C'est une methode particulière liée au Thread.
    def run(self):
        count = 0
        while not self._stop_flag: # Tant qu'on n'arrête pas ça tourne.
            try:
                msg = self._interface.read()    # Lit une trame.

                # Si on a une trame d'arrivée.
                if self._output_fd is not None: # Si on a une trame d'arrivée.
                    self._output_fd.write(f"{msg.TimeStamp} {msg.Id:08X} {msg.data.hex(" ")}\n")
                # Sinon on ne fait rien.
                
                # Si on a le thread en cours   
                if self._update_callback is not None:
                    self._update_callback(count, msg)
                count += 1 # Compte le nombre de scutation
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
    def __init__(self,status):

        # self._colonne_2 = None
        # self._status_data = None
        #  self._designation = None    # => désignation à plusieurs valeurs variable de boucle ?
        self._treeview = None
        self._lab_status = None
        # self._index = None
        # self._element = None
        
        self._status = status # ????
        self._status = tk.Tk() # Crée une nouvelle fenêtre On ecrase la variable direct ?
        self._status.title("Etats")
        self._status.geometry("230x205")


        # Utiliser la suppresion des instances de cette fenêtre sur fermeture
        # Car il ne supporte pas de la regénéré au niveau du TreeView

        """
        def fermer(self):
            print(f"Fermeture de la fenêtre avec le statut '{self._status}'...")
            self._status.destroy()

        self._status.protocol("WM_DELETE_WINDOW", self.fermer)  # Gestion de la fermeture
        """


        # Créer un Treeview
        self._colonnes = ("Colonne 1", "Colonne 2")
        self._treeview = ttk.Treeview(self._status, columns=self._colonnes, show="headings")

        # Définir les en-têtes des colonnes
        self._treeview.heading("Colonne 1", text="Etat")
        self._treeview.heading("Colonne 2", text="")

        # Définir les largeurs des colonnes
        self._treeview.column("Colonne 1", width=150)
        self._treeview.column("Colonne 2", width=20)

        # Afficher le Treeview
        self._treeview.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        print("TreeView Installé")

    _status_data = (
        ("Pas de défaut", CANSTATUS_NO_ERROR),
        ("Buffer de reception plein", CANSTATUS_RECEIVE_FIFO_FULL),
        ("Buffer de transmission plein", CANSTATUS_TRANSMIT_FIFO_FULL),
        ()
    )

    def remplir_treeview(self,status):
        # self._status = status  # pourquoi affecter le paramètre ? En plus status est une sous-fenêtre
        # Liste des erreurs possibles
        """
        self._status_data = [
            {"designation": "Pas de défaut", "Lab_Status": CANSTATUS_NO_ERROR},
            {"designation": "Buffer de reception plein", "Lab_Status": CANSTATUS_RECEIVE_FIFO_FULL},
            {"designation": "Buffer de transmission plein", "Lab_Status": CANSTATUS_TRANSMIT_FIFO_FULL},
            {"designation": "Avertissement erreur", "Lab_Status": CANSTATUS_ERROR_WARNING},
            {"designation": "Surcharge des Données", "Lab_Status": CANSTATUS_DATA_OVERRUN},
            {"designation": "Erreur passive", "Lab_Status": CANSTATUS_ERROR_PASSIVE},
            {"designation": "Défaut d'arbitrage", "Lab_Status": CANSTATUS_ARBITRATION_LOST},
            {"designation": "Erreur sur le bus", "Lab_Status": CANSTATUS_BUS_ERROR},
        ]
        ici le dictionaire est inutile, à quoi sert le Lab_status ?
        si c'est statique, on ne le met pas en instance mais au niveau classe => voir début plus haut
        """


        # Parcourir les éléments et vérifier les correspondances avec le status actuel
        for index, element in enumerate(self._status_data):
            designation = element[0]  # il faut simplifier
            colonne_2 = "X" if (status == 0 and index == 0) else ""
            print(f"Insertion : {designation}, Colonne 2 : {colonne_2}")

            # Insérer dans le TreeView
            if self._treeview:
                self._treeview.insert("", tk.END, values=(designation, colonne_2))
            else:
                print("TreeView non initialisé.")
# *************************************** FIN DE LA FENETRE STATUS *****************************************************

# *********************************** FENETRE PRINCIPALES **************************************************************
class MainWindow:

    # Fonction de creation de la fenêtre principale
    def __init__(self):

        self._FentreStatus = None
        self._status = None
        self._root = tk.Tk()
        self._root.title("LECTURE DES TRAMES EN TEMPS REEL")
        self._root.geometry("600x386")

        frame = tk.Frame(self._root)
        frame.place(x=50, y=100)

        # On initialyse les variables
        self._can_interface = None
        self._reader = None
        self.fichier_chemin = None
        self.result = False
        self._FenetreStatus = None

        # créé l'interface avec le CAN
        try:
            self._can_interface = WindowsUSBCANInterface()
        except CanError:
            raise

        # =============== ALJOUT DES CONTROLES SUR LA FENETRE ===============================

        # Ajout d'un bouton OPEN et défini sa taille puis défini son emplacement
        self.button_open = tk.Button(self._root, text="Open", width=10, height=1, command=self.on_open_click)
        # button.pack(pady=20)
        self.button_open.place(x=10, y=40)

        # Ajout d'un bouton READ et défini sa taille puis défini son emplacement
        self.button_read = tk.Button(self._root, text="Read", width=10, height=1, command=self.on_read_click)
        self.button_read.place(x=10, y=80)

        # Ajout d'un bouton CLOSE et défini sa taille puis défini son emplacement
        self.button_close = tk.Button(self._root, text="Close", width=10, height=1,  state='disabled',command=self.on_close_click)
        self.button_close.place(x=100, y=40)

        self.button_stop = tk.Button(self._root, text="Arrêter", width=10, height=1, command=self.on_stop_click)
        self.button_stop.pack()
        self.button_stop.place(x=200, y=80)
        
        # Ajouter un bouton pour ouvrir la fenêtre des états
        self.button_status = tk.Button(self._root, text="États", width=10, height=1, command=self.on_status_click)
        self.button_status.place(x=10, y=120)
        

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
        # self._can_interface = WindowsUSBCANInterface()  # Ca devrait disparaitre ???? car défini sur le constructeur

        # Appelle cette fonction de manière explicite
        #  Le handle ne sert à rien et il ne faut pas que la feb^tre le connaisse
        # pas besoin de mettre les valeurs par défaut
        # self._handle = self._can_interface.open(CAN_BAUD_250K,CANUSB_ACCEPTANCE_MASK_ALL,CANUSB_ACCEPTANCE_MASK_ALL,CANUSB_FLAG_TIMESTAMP)
        
        # print(f"Résultat de l'appel : {self._handle}")
        try:
            self._can_interface.open() # les paramètres sont par défaut
            self.disable_button_open()    # Met le bouton d'ouverture en disabled
            self.enable_button_close()
            self.enable_button_read()
            print("C'est ouvert ...........")
            self.result=True  # result sert à savoir si le open est OK, non ?
        except CanError:
            print("PAS BON !!!")

    def on_stop_click(self):
        # Met fin à la boucle
        if self._reader is not None:
            self._reader.stop()             # Arrête la lecture
            print ("Le read est arrêté")
            self._reader = None
            self.enable_button_open()
            self.disable_button_close()
            self.on_close_click()           # Ferme la laison



    def on_read_click(self):    # Lit en temps réel
        print("Bouton cliqué ! Voici votre programme de lecture.")

        self.disable_button_read()   # Desactive le bouton READ
        # Appelle la fonction de lecture en temps réel
        # CE N'EST PAS NORMAL D'ENREGITRER
        # CAR ON PEUT SIMPLEMENT LIRE LES TRAMES ET PAS LES ENREGISTRER
        self._reader = CANUSBReader(self._can_interface, self.update_read, self.fichier_chemin)

        # Lance le Theard.
        self._reader.start()

    # Fonction en callback. Appelé par CANUSBReader
    def update_read(self, compteur, msg):
        self.label.config(text=f"Compteur : {compteur}") # Affiche le nombre de trames reçues
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
        if self.result:
            self.enable_button_open()       # Active le bouton d'ouverture
            self.on_stop_click()            # Arrête la boucle
            self._can_interface.close()     # Ferme l'adaptateur
            self.disable_button_close()


        result = False

    def choix_fichier(self):
        # Ouvrir une boîte de dialogue pour sélectionner un fichier
        self.fichier_chemin = filedialog.asksaveasfilename(
            title="Choisissez le fichier à enregistrer",
            filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")),
            defaultextension=".txt"
        )

    def initialize_status(self):
        if self._FenetreStatus is None:
            status = self._can_interface.status()
            self._FenetreStatus = FenetreStatus(status)

    def on_status_click(self):
        try:
            if self.result:
                self.initialize_status()
                status = self._can_interface.status()  # Récupérer le statut actuel
                print(f"Remplir TreeView avec le statut: {status}")
                self._FentreStatus.remplir_treeview(status)  # Mettre à jour le TreeView
        except Exception as e:
            print(f"Erreur : {e}")
    # =================== FIN DES FONCTIONS ======================
# **********************************************************************************************************************
    
    # Cette fonction s'éxécute sur le lancement qui est défini ci aprés, suit le principe des déclarations.
    def open(self):
        self._root.mainloop()

# Lance la Mainwindow
if __name__ == "__main__":
    main_window = MainWindow()
    main_window.open()

# ======================================================================================================================

