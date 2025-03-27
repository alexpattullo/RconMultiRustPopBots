import multiprocessing
import asyncio
import discord
from discord.ext import commands
import shared_resources
import random
import json

class GlobalPop(commands.Bot):
     def __init__(self):
          super().__init__(intents=None,command_prefix=":;1l434",help_command=None)

     async def on_ready(self):
          print(f"Logged in as {self.user}")

     async def active_task(self):
          await self.wait_until_ready()
          while True:
               #Run the task every x seconds
               await asyncio.sleep(shared_resources.GEN_CONFIG['RefreshRate'])

               #Check the bot is online and connected
               if self.is_closed() or not self.is_ready() or not self.ws:
                    continue


               try:
                    global_players = 0
                    global_maxplayers = 0
                    global_joining = 0
                    global_queued = 0

                    #Go through each server
                    for s in shared_resources.Active_Rcon_Connections:
                         server = shared_resources.Active_Rcon_Connections[s]

                         #Server Offline
                         if not server.server_rcon_connection:
                              continue     
                         
                         #Server Online
                         #Get the pop
                         response = await server.run_a_raw_command("serverinfo",random.randint(50,9999))
                         if not response:
                              continue

                         #PopInfo
                         resp_dict = json.loads(response)
                         resp_msg = json.loads(resp_dict["Message"])
                         
                         global_players += resp_msg["Players"]
                         global_maxplayers += resp_msg["MaxPlayers"]
                         global_joining += resp_msg["Joining"]
                         global_queued += resp_msg["Queued"]

                    #Population Info
                    population_info = f"{global_players} Players"

                    #If Q
                    if global_queued > 0:
                         population_info += f" (+{global_queued} Queued)"

                    #If Joining
                    else:
                         if global_joining > 0:
                              population_info += f" ⇋ {global_joining} Joining!"
                    
                    
                    if population_info == f"{global_players} Players":
                         population_info = f"{global_players} Players Ingame!"
                    
                    
                    #Change the actual bot status
                    await self.change_presence(
                         status=discord.Status.online,
                         activity=discord.Activity(
                              type=discord.ActivityType.custom,
                              name=population_info,
                              state=population_info
                         )
                    )
               except ConnectionResetError as e:
                    continue

   
               
    
     async def setup_hook(self):
          self.loop.create_task(self.active_task())  # Start the background task

