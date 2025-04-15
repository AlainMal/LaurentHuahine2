
# Cette classe sert uniquement à traiter les résultats, il n'y a pas de self.
# C'est pévu de la faire traiter le NMEA 2000.
class TraitementCAN:
    def __init__(self):
          pass

    @staticmethod
    async def enregistrer(msg, file_path, coche,main_window):
        print("tttttt")
        # Initialise data comme un str vide.
        datas = ""
        # On va définir les huits octets dans "datas".
        for i in range(msg.len):
            # On commence par un espace, car ça fini par le dernier octet.
            datas += " " + format(msg.data[i], "02X")

        # on met le résultat dans la table.
        if msg:
            trame_list = [(f"{msg.ID:08X}", f"{msg.len} {datas}")]
            main_window.affiche_trame(trame_list)
        # On met le réulltat dans un fichier
        if msg and coche:
            with open(file_path, "w") as file:
                file.write(f"{msg.TimeStamp} {msg.ID:08X} {msg.len}{datas}\n")
