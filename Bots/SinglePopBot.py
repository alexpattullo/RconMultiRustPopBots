import multiprocessing
import asyncio
import discord
from discord.ext import commands
import random
import json
import shared_resources

class SinglePopBot(commands.Bot):
     def __init__(self,name:str):
          super().__init__(intents=None,command_prefix=":;1l434",help_command=None)
          self.name = name

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
                    #Find our server in the rcon connections
                    server = shared_resources.Active_Rcon_Connections.get(self.name)
                    if not server:
                         raise Exception(f"Server {self.name} not found in Active_Rcon_Connections - make sure servernames are unique")
     
                    #Server Offline
                    if not server.server_session or (server.server_session and server.server_session.closed):
                         await self.change_presence(
                              status=discord.Status.do_not_disturb,
                              activity=discord.Activity(
                                   type=discord.ActivityType.custom,
                                   name="[Server Offline]",
                                   state="[Server Offline]"
                              )
                         ) 
                         continue
                    
                    #Server is online but no rcon connection ie booting
                    if server.server_session and not server.server_rcon_connection:
                         await self.change_presence(
                              status=discord.Status.do_not_disturb,
                              activity=discord.Activity(
                                   type=discord.ActivityType.custom,
                                   name="Establishing Connection...",
                                   state="Establishing Connection..."
                              )
                         ) 
                         continue

                    #Server Online
                    #Get the pop
                    response = await server.run_a_raw_command("serverinfo",random.randint(50,9999))

                    #Servers up but no reply to serverinfo
                    if server.server_session and server.server_rcon_connection and not response:
                         await self.change_presence(
                              status=discord.Status.idle,
                              activity=discord.Activity(
                                   type=discord.ActivityType.custom,
                                   name="Server Booting...",
                                   state="Server Booting...."
                              )
                         ) 
                         continue
                    elif not response:
                         continue


                    #PopInfo
                    resp_dict = json.loads(response)
                    resp_msg = json.loads(resp_dict["Message"])
                    
                    players = resp_msg["Players"]
                    maxplayers = resp_msg["MaxPlayers"]
                    joining = resp_msg["Joining"]
                    queued = resp_msg["Queued"]

                    population_info = ""
                    
                    #Standard format
                    population_info += f"{players}/{maxplayers}"

                    #If Q
                    if queued > 0:
                         population_info += f" ({queued} queued)"
                    
                    #If Joining
                    else:
                         if joining > 0:
                              population_info += f" ⇋ {joining} Joining!"

                    #if population_info == f"{players}/{maxplayers}":
               #     population_info = f"{players}/{maxplayers} Connected!"

                    
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

