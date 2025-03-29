import tkinter as tk
from tkinter import Checkbutton, BooleanVar,ttk
from threading import Thread
import ctypes
from Package.CANUSB import canusb_Open, canusb_Read, CanMsg, canusb_Close
from Package.Fonctions_USBCAN import enregistre, choix_fichier

# Fonction de creation de la fenêtre principale
def create_window_principal():
    root = tk.Tk()
    root.title("LECTURE DES TRAMES EN TEMPS REEL")
    root.geometry("600x386")

    frame = tk.Frame(root)
    frame.place(x=50, y=100)

    # ========== FONCTIONS D'ACTIVATION ET DESACTIVATION DES BOUTONS ==========
    def disable_button_open():
        button_open['state'] = 'disabled'  # Désactive le bouton

    def enable_button_open():
        button_open['state'] = 'normal'  # Active le bouton

    def disable_button_read():
        button_read['state'] = 'disabled'  # Désactive le bouton

    def enable_button_read():
        button_read['state'] = 'normal'  # Active le bouton
    # =========================================================================

    # =================== FONCTIONS DES CONTROLES SUR LA FENETRE ======================
    # Fonction sur OPEN click
    def on_open_click():
        global handle  # Le handle est une variable global, utilisé par les autres fonctions

        print("Bouton cliqué ! Voici un programme d'ouverture.")
        # Appeler la fonction
        szID = None  # Exemple d'ID en bytes
        szBitrate = b"250"  # Exemple de taux de transmission en bytes
        acceptance_code = 0x0
        acceptance_mask = 0xFFFFFFFF
        flags = 0x1

        # Exécution de la fonction OPEN
        handle = canusb_Open(szID, szBitrate, acceptance_code, acceptance_mask, flags)
        print(f"Résultat de l'appel : {handle}")
        if handle:                  # Si c'est ouvert
           disable_button_open()    # Met le bouton d'ouverture en disabled
           result=True
        else:
            print("PAS BON le HANDLE")

    def on_stop_click():
        global stop_loop
        stop_loop = True  # Met fin à la boucle
        enable_button_read()

    def on_read_click():    # Lit en temps réel
        print("Bouton cliqué ! Voici votre programme de lecture.")
        try:
            # Vérifier si le handle est valide
            if handle:
                print("CA RECOIT")
                # Créer une instance de la structure CanMsg
                msg = CanMsg()

                global stop_loop    # Variable globale pour arrêter la boucle
                stop_loop = False   # Réinitialise la condition d'arrêt
                compteur = 0
                disable_button_read()   # Desavtive le boutpn READ
                # Appelle la fonction de lecture en temps réel
                while not stop_loop:
                    result = canusb_Read(handle, ctypes.byref(msg))

                    # enregistre(msg, tree, check_enr)    # A SUPPRIMER *******************
                    if result == 1:
                        # Appel la fonction pour enregistrer et afficher sur la TreeView
                        enregistre(msg,tree,check_enr)
                        compteur += 1
                        label.config(text=f"Compteur : {compteur}")
                    else:
                        """
                        print(f"ID: {msg.ID}")
                        print(f"TimeStamp: {msg.TimeStamp}")
                        print(f"Flags: {msg.flags}")
                        print(f"Length: {msg.len}")
                        print("Data:", list(msg.data))
                        """

                    root.update()   # Donne la main au systême

                stop_loop=True


        except Exception as e:
            print(f"Exception sur le handle : {e}")

    def on_checkbox_change():
        if check_enr.get():  # Si la case est cochée
            print("Checkbox cochée - Enregistrement activé")
            # Pour récupérer le chemin et créer un nouveau fichier
            fichier_chemin = choix_fichier()

        else:  # Si la case est décochée
            fichier_chemin = None
            print("Checkbox décochée - Enregistrement désactivé")

    def on_close_click():
        on_stop_click()         # Arrête le boucle
        canusb_Close(handle)    # Ferme l'adaptateur
        enable_button_open()    # Active le bouron d'ouverture
        result = False

    # ==================================================================================

    # =============== ALJOUT DES CONTROLES SUR LA FENETRE ===============================
    # Ajout d'un bouton OPEN et défini sa taille puis défini sont emplacement
    button_open = tk.Button(root, text="Open", width=10, height=1, command=on_open_click)
    # button.pack(pady=20)
    button_open.place(x=10, y=40)

    # Ajout d'un bouton CLOSE et défini sa taille puis défini sont emplacement
    button_close = tk.Button(root, text="Close", width=10, height=1, command=on_close_click)
    button_close.place(x=100, y=40)

    # Ajout d'un bouton READ et défini sa taille puis défini sont emplacement
    button_read = tk.Button(root, text="Read", width=10, height=1, command=on_read_click)
    button_read.place(x=10, y=80)

    button_stop = tk.Button(root, text="Arrêter", width=10, height=1, command=on_stop_click)
    button_stop.pack()
    button_stop.place(x=200, y=80)


    # Ajput d'une CheckBox
    check_enr = BooleanVar()
    check_enregistre = tk.Checkbutton(root,text="Enregistrer",variable=check_enr,command=on_checkbox_change)
    check_enregistre.place(x=100, y=80)  # Coordonnées précises en pixels

    # Ajout un TreeView avec 3 colonnes
    tree = ttk.Treeview(root, columns=("ID", "Length", "Data"), show="headings", height=18)
    # Positionner le Treeview et la Scrollbar
    tree.place(x=330, y=0)

    # Ajout des en-têtes des colonnes
    tree.heading("ID", text="ID")
    tree.heading("Length", text="Len")
    tree.heading("Data", text="Data")

    # Ajuster la taille des colonnes
    tree.column("ID", width=70)
    tree.column("Length", width=30)
    tree.column("Data", width=150)

    # Ajout d'une verticale scrollbar sur la fenêtre
    scrollbar = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')


    # Ajouter un label
    label = tk.Label(root, text="Affichage du nombre de trames", width=40 , anchor='w')
    label.place(x=5, y=10)

    # ====================== FIN DES CONTROLES ======================================


    # ==============================================================================
    # Démarrer la boucle principale de l'interface graphique
    root.mainloop()
    # ==============================================================================

# ================= DEMARRAGE DU THREAD ===========================================
def run_thread():
    # Créer et démarrer un thread pour la fenêtre
    thread = Thread(target=create_window_principal)
    thread.start()

# Lance le Thread
if __name__ == "__main__":
    run_thread()
# =================================================================================

