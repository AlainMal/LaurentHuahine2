
# Cette classe sert uniquement à traiter les résultats, il n'y a pas de self.
# C'est prévu de lui faire traiter le NMEA 2000 en temps réel.
# ======================================================================================================================
class TraitementCAN:
    def __init__(self):
          pass

    @staticmethod
    async def enregistrer(msg, file_path, coche,main_window):
        # print("On entre dans l'enregistement")
        # Initialise datas comme un str vide.
        datas = ""
        # On a défini les huits octets dans "datas".
        for i in range(msg.len):
            # On commence par un espace, car ça fini par le dernier octet.
            datas += " " + format(msg.data[i], "02X")

        # on met le résultat dans la table.
        """   Ca ne fonctionne pas car il est trop lent et ça loupe des trames.
        if msg:
            trame_list = [(f"{msg.ID:08X}", f"{msg.len}", f"{datas}")]
            # print("On a calculé la liste prête à être affiché sur le tableau")
            main_window.affiche_trame(trame_list)
        """
        # On met le réulltat dans un fichier si la case à cocher est validée.
        if msg:
            if coche:
                with open(file_path, "a") as file:
                    file.write(f"{msg.TimeStamp} {msg.ID:08X} {msg.len}{datas}\n")

            # ATTENT POUR Y INCLURE LES DATAS **********************
