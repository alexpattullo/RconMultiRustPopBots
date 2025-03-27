import json
Active_Rcon_Connections = {}

#Fetch config file
with open("./config.json", "r") as file:
    GEN_CONFIG = json.load(file)


