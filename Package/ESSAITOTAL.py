
import subprocess
import multiprocessing
from tkinter import BooleanVar, ttk, filedialog, messagebox
from Package.CANUSB import  WindowsUSBCANInterface, CanError
from Package.constante import *
from Package.NMEA_2000 import *
from Package.VoirResult import *

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

    def remplir_treeview(self):
        # La liste des différents défauts
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
class MainWindow(tk.Tk):
    def __init__(self, queue):
        super().__init__()

        self.title("TEMPS REEL")
        self.geometry("290x386")

        self.FenetreAppercu = None


        self._can_interface = None
        self._reader = None
        self.fichier_chemin = None
        self._handle = None

        self._FenetreStatus = None
        self._status = None

        # créé l'interface avec le CAN
        try:
            self._can_interface = WindowsUSBCANInterface(self)
            self._nmea2000 = NMEA2000()
        except CanError:
            raise

        self._stop_flag = True

        self.queue = queue # Ajout de la queue


        # ====================== ALJOUT DES CONTROLES SUR LA FENETRE ===============================
        # Ajout d'un bouton OPEN et défini sa taille puis défini son emplacement
        self.button_open = tk.Button(self, text="Open", width=10, height=1, command=self.on_open_click)
        # button.pack(pady=20)
        self.button_open.place(x=10, y=40)

        # Ajout d'un bouton READ et défini sa taille puis défini son emplacement
        self.button_read = tk.Button(self, text="Read", width=10, height=1,state='disabled', command=self.on_read_click)
        self.button_read.place(x=10, y=80)

        # Ajout d'un bouton CLOSE et défini sa taille puis défini son emplacement
        self.button_close = tk.Button(self, text="Close", width=10, height=1, state='disabled', command=self.on_close_click)
        self.button_close.place(x=100, y=40)

        # Ajout d'un bouton pour ouvrir la fenêtre des états
        self.button_status = tk.Button(self, text="États", width=10, height=1, command=self.on_status_click)
        self.button_status.place(x=10, y=120)

        # Ajout d'un bouton pour afficher le fichier .txt.
        self.button_fichier = tk.Button(self, text="...", width=2, height=1, command=self.on_fichier_click)
        self.button_fichier.place(x=10, y=160)

        # Ajout d'un bouton pour afficher le fichier .txt.
        self.button_stop = tk.Button(self, text="Arrêter", width=10, height=1,state='disabled', command=self.on_stop_click)
        self.button_stop.place(x=200, y=80)

        # Ajout d'un bouton pour afficher la fenêtre "Apperçu"
        self.button_voir = tk.Button(self, text="Voir ...", width=10, height=1, state='normal', command=self.on_voir_click)
        self.button_voir.place(x=100, y=340)

        # Ajout d'un label qui affiche le PGN en cours
        self.lab_pgn = tk.Label(self, text="PGN en cours", width=40, anchor='w')
        self.lab_pgn.place(x=100, y=220)

        # Ajout d'un label qui affiche la Source en cours
        self.lab_src = tk.Label(self, text="Source en cours", width=40, anchor='w')
        self.lab_src.place(x=100, y=240)

        # Ajout d'un label qui affiche la Destination en cours
        self.lab_dest = tk.Label(self, text="Destination en cours", width=40, anchor='w')
        self.lab_dest.place(x=100, y=260)

        # Ajout d'un label qui affiche la Priorité en cours
        self.lab_prio = tk.Label(self, text="Priorité en cours", width=40, anchor='w')
        self.lab_prio.place(x=100, y=280)

        # Ajput d'une CheckBox qui permet d'enregistrer le fichier
        self.check_enr = BooleanVar()
        check_enregistre = tk.Checkbutton(self, text="Enregistrer", variable=self.check_enr,command=self.on_checkbox_change)
        check_enregistre.place(x=100, y=80)  # Coordonnées précises en pixels

       # Ajout d'un label qui affiche le nombre de scrutations
        self.label = tk.Label(self, text="Affichage du nombre de trames reçues ", width=40, anchor='w')
        self.label.place(x=5, y=10)

        # Ajout d'un label qui affiche le fichier en cours
        self.lab_fic = tk.Label(self, text="Fichier en cours", width=40, anchor='w')
        self.lab_fic.place(x=40, y=160)

        self.update_data()  # Lancer l'actualisation en boucle

    def update_data(self):
        if not self.queue.empty():
            data = self.queue.get()
            self.label.config(text=f"Données reçues : {data.hex()}")  # Affichage en hexadécimal
        self.after(10, self.update_data)  # Vérification toutes les 10 ms
        # ====================== FIN DES CONTROLES ======================================



    # ========== METHODES D'ACTIVATION ET DESACTIVATION DES BOUTONS ==========
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

    # =================== METHOOES DES CONTROLES SUR LA FENETRE ======================
    # Fonction sur OPEN click
    def on_open_click(self):
        print("Bouton cliqué ! Voici un programme d'ouverture.")

        # Exécution de la fonction OPEN
        self._can_interface = WindowsUSBCANInterface(self)

        # Appelle cette fonction de manière explicite et la fait passer sur "interface".
        self._handle = self._can_interface.open(CAN_BAUD_250K, CANUSB_ACCEPTANCE_MASK_ALL, CANUSB_ACCEPTANCE_MASK_ALL,
                                                CANUSB_FLAG_TIMESTAMP)

        print(f"Résultat de l'appel : {self._handle}")

        if self._handle:  # Si l'adaptateur est ouvert.
            self.disable_button_open()  # Met le bouton d'ouverture en disabled
            self.enable_button_close()
            self.enable_button_read()
            print("C'est ouvert ...........")
        else:
            print("PAS BON !!!")
            messagebox.showinfo("OUVERTURE DE L'ADAPTATEUR", "Vérifiez que vous êtes bien raccordé")

    def on_close_click(self):
        if self._reader is not None:
            # Arrête la lecture
            self._reader.stop()
            # self._reader.join()
            if self._handle is not None:
                self._can_interface.close()  # Ferme l'adaptateur
                self.enable_button_open()  # Active le bouton d'ouverture
                self.disable_button_close()
                self.disable_button_read()
                self.disable_button_stop()


            print("Le read est arrêté")
            self._reader = None

    def on_read_click(self):  # Lit en temps réel
        print("Bouton cliqué ! Voici votre programme de lecture.")
        if self._handle:
            self.disable_button_read()  # Desactive le bouton READ
            self._stop_flag = False
            # self.start_process()
            # Appelle la fonction de lecture en temps réel
            # self._reader = CANUSBReader(self._can_interface, self.update_read, self.fichier_chemin)

            # Lance le Theard.
            # self._reader.start()
            self.enable_button_stop()

    # Fonction en callback. Appelé par la classe CANUSBReader
    def update_read(self, compteur, tuple):
        self.label.config(text=f"Compteur : {compteur}")  # Affiche le nombre de trames reçues du Read.

        # A SUPPRIMER
        self.lab_pgn.config(text=f"PGN1              : {tuple[0]}")  # Affiche le PGN1.
        self.lab_src.config(text=f"Valeur           : {tuple[3]}")  # Affiche la Valeur
        self.lab_pgn.config(text=f"PGN2             : {tuple[1]}")  # Affiche le PGN1.
        self.lab_src.config(text=f"Valeur           : {tuple[4]}")  # Affiche la Valeur

        if self.FenetreAppercu:  # Vérifie que la fenêtre est bien ouverte
            self.FenetreAppercu.ecrit("poiuytre", 5)


        self.update()

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
            self._FenetreStatus.remplir_treeview()  # Mettre à jour la TreeView
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

    def ouvre_fichier(self):
        # Ouvrir une boîte de dialogue pour sélectionner un fichier
        self._file = filedialog.asksaveasfilename(
            title="Choisissez le fichier à enregistrer",
            filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")),
            defaultextension=".txt")
        self._output_fd = open(self._file, "w")

    def on_fichier_click(self):
        try:
            if self.fichier_chemin is not None:
                # Afficher la boîte de dialogue YES NO CANCEL
                reponse = messagebox.askyesnocancel("OUVRIR UN FICHIER", "Voulez-vous examiner le fichier ?,\nSinon en créer un autre")

                if reponse is True:
                    # Affiche le fichier dans la notebloc
                    subprocess.Popen(["notepad", self.fichier_chemin])
                elif reponse is False:
                    self.ouvre_fichier()
                    if self.fichier_chemin != "":
                        print("Fichier :" + str(self.fichier_chemin))
                        # Incrit le fichier sur l'écran.
                        self.lab_fic.config(text=f"Fichier : {self.fichier_chemin}")
            else:
                # Ouvrir la boîte de dialogue pour sélectionner un fichier
                self.ouvre_fichier()
                if self.fichier_chemin == "":
                    self.fichier_chemin= None
                else:
                    print("Fichier :" + str(self.fichier_chemin))
                    # Incrit le fichier sur l'écran.
                    self.lab_fic.config(text=f"Fichier : {self.fichier_chemin}")

        except Exception as e:
            print(f" : {e}")

    # Méthode pour afficher la fenêtre résultat
    def on_voir_click(self):
        if not self.FenetreAppercu:
            self.FenetreAppercu = FenetreAppercu()

def producer(self,queue):
    print("Produce bien lancé")
    while not self._stop_flag:  # Tant qu'on n'arrête pas, ça tourne.
        try:

            # Voir la boucle dans la class WindowsUSBCANInterface dans CANUSB.
            self._msg = self._can_interface.read(self._stop_flag)  # Lit une trame, quand il y a en une, donc on attend.

            # *********************************************************************************************
            #                    C'EST ICI QUE L'ON MET L'INTERPRETEUR À QUI ON ENVOI LE MSG
            # *********************************************************************************************
            # Appel la fonction qui renvoi un tuple sur l'ID, cette fonction doit disparaitre.
            self.tuple_id = self._nmea2000.id(self._msg)

            # Appel la fonction qui retourne le tuple de tous les résultats
            self._resultat = self._nmea2000.tuple_octets(self._msg)
            # print(self._resultat)

            # Il manque encore la fonction qui envoi sur la fenêtre FenetreAppercu.

            # **********************************************************************************************

            # Si on a le fichier ouvert. On enregistre quand il y a un msg.
            if self._output_fd is not None:
                datas = ""
                # On va définir les octets dans "datas".
                for i in range(self._msg.len):
                    # On commence par un espace, car ça fini par le dernier octet.
                    datas += " " + format(self._msg.data[i], "02X")

                # On ne met pas d'espace entre len et datas, voir les datas ci-dessus.
                self._output_fd.write(f"{self._msg.TimeStamp} {self._msg.ID:08X} {self._msg.len:08X}{datas}\n")

            # Si on a le thread en cours, On renvoie la valeur du count et du tuple_résultat

        except CanError as err:
            print("Erreur CAN", err)
            break
        except IOError as err:
            print("Erreur fichier", err)
        except Exception as err:  # catch all => à enlever
            print("Exception:", err)
            break

        # Sinon on ferme le fichier et on ferme l'interface
        # self.close_file()
        self._can_interface.close()


    def start_process(self):
        """Lance le processus de `producer`"""
        self._stop_flag = False
        self.queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(target=self.producer, args=(self.queue,))
        self.process.start()


    def stop_process(self):
        """Arrête le processus en mettant _stop_flag à True"""
        self._stop_flag = True
        if self.process:
            self.process.terminate()
            self.process.join()

    # Méthode appelée sur fermeture de la fenêtre principale"
    def fermer_MainWindow(self):
        self.on_close_click()
        messagebox.showinfo("AU REVOIR...","A la prochaine :)")
        self.destroy()  # Fermer la fenêtre
    # ======================================= FIN DES METHODES ==================================================

if __name__ == "__main__":
    main_window = MainWindow(queue)
    main_window.mainloop()