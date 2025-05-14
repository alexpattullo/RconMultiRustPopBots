import json
Active_Rcon_Connections = {}

#Fetch config file
with open("./testconfig.json", "r") as file:
    GEN_CONFIG = json.load(file)


