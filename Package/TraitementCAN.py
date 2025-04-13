class TraitementCAN:
    def __init__(self):
          pass

    async def enregistrer(self,msg,file_path):
        # print("Message CAN reçu :", msg)
        datas = ""
        # On va définir les octets dans "datas".
        for i in range(msg.len):
            # On commence par un espace, car ça fini par le dernier octet.
            datas += " " + format(msg.data[i], "02X")
            # On ne met pas d'espace entre len et datas, voir les datas ci-dessus.
            with open(file_path, "w") as file:
                file.write(f"{msg.TimeStamp} {msg.ID:08X} {msg.len:08X}{datas}\n")




