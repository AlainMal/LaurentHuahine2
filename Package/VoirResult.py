import tkinter as tk

class FenetreAppercu:
    def __init__(self):
        self._fenetre_appercu = tk.Tk()  # Création de la fenêtre
        self._fenetre_appercu.title("Apperçu des valeur en temps réel")
        self._fenetre_appercu.geometry("830x405")


        frame1 = tk.Frame(self._fenetre_appercu, width=200, height=600)
        frame1.pack(padx=10, pady=10)
        frame1.place(x=10, y=10)

        # Ajouter les commentaires et les zones de texte
        labels = ["Vitesse du vent", "Direction du vent", "COG", "SOG","Heading", "Profondeur", "Volts batterie", "Ampères Batterie", "Température Batterie", "Lattitude", "Longitude", "Presion atmosphèrique"]  # Liste des commentaires
        textboxes1 = []  # Pour stocker les textbox

        for i, label_text in enumerate(labels):
            # Créer un commentaire (Label)
            label = tk.Label(frame1, text=label_text, font=("Arial", 10))
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")  # Aligné à droite (sticky="e")

            # Créer une textbox
            textbox = tk.Text(frame1, height=1, width=10)
            textbox.grid(row=i, column=1, padx=5, pady=5)  # Alignée à droite du commentaire

            # Stocker la textbox pour un usage ultérieur
            textboxes1.append(textbox)

        frame2 = tk.Frame(self._fenetre_appercu, width=200, height=600)
        frame2.pack(padx=10, pady=10)
        frame2.place(x=350, y=10)

        # Ajouter les commentaires et les zones de texte
        labels = ["Niveau d'eau douce", "Total eau douce", "Niveau Gasoil", "Total Gasoil"]  # Liste des commentaires
        textboxes2 = []  # Pour stocker les textbox

        for i, label_text in enumerate(labels):
            # Créer un commentaire (Label)
            label = tk.Label(frame2, text=label_text, font=("Arial", 10))
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")  # Aligné à droite (sticky="e")

            # Créer une textbox
            textbox = tk.Text(frame2, height=1, width=10)
            textbox.grid(row=i, column=1, padx=5, pady=5)  # Alignée à droite du commentaire

            # Stocker la textbox pour un usage ultérieur
            textboxes2.append(textbox)





