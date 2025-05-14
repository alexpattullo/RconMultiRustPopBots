import json
import discord
import aiohttp
import asyncio
from datetime import datetime
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
import random
import aiohttp
import asyncio
from datetime import datetime


class RconManager:
     def __init__(self, ip: str, port: int, password: str, nickname: str = "Unknown"):
        self.ip = ip
        self.port = port
        self.password = password
        self.nickname = nickname

        self.first_connection = True

        self.server_session = None
        self.server_rcon_connection = None

        self.reconnect_task = None  # Task for managing reconnections
        self.rcon_messages_task = None #Task to deal with rcon messages

        
        self.pending_responses = {}

     async def attempt_server_login(self):
        # Attempt Connection
         # print(f"🔄 Attempting to connect to {self.ip}:{self.port} {self.nickname}...")
          try:
               session = aiohttp.ClientSession()
               server_rcon = await session.ws_connect(f"ws://{self.ip}:{self.port}/{self.password}", timeout=5)

          except Exception as e: #(ConnectionRefusedError, aiohttp.ClientConnectorError, asyncio.TimeoutError) using all as random ones occuring not seen before
               #print(f"❌ : Failed to connect to {self.ip}:{self.port} {self.nickname}. Error: {e}")
               if session:
                    await session.close()
               return None, None


          # Valid Connection
          server_rcon._timeout = None  # Disable the default timeout
          print(f"✅ : RCON CONNECTED - {self.ip}:{self.port} {self.nickname}  @ {datetime.now().strftime('%H:%M:%S')}")
          return session, server_rcon

     async def manage_server_connection(self):
          while True:
               self.server_session, self.server_rcon_connection = await self.attempt_server_login()
               if self.server_rcon_connection and self.server_session:
                    # Connection successful, break out of reconnection loop
                    break
               #print(f"🔄 : Retrying connection to {self.ip}:{self.port} {self.nickname}...")
               await asyncio.sleep(5)  # Retry after 5 seconds if connection fails



     async def maintain_connection(self):
          """Ensure that the connection stays alive, reconnect if dropped."""
          while True:
               #No connection or connection closed & not initial connection
               if not self.server_rcon_connection or self.server_rcon_connection.closed:
                    if not self.first_connection:

                         ### CONNECTION LOST ###
                         print(f"⚠️ : Lost connection to {self.ip}:{self.port} {self.nickname} {datetime.now()}, attempting to reconnect...")


                         #End Tasks
                         if self.rcon_messages_task and not self.rcon_messages_task.done():
                              self.rcon_messages_task.cancel()
                              try:
                                   await self.rcon_messages_task
                              except asyncio.CancelledError:
                                   pass

                         #Close the current session
                         if self.server_session:
                              await self.server_session.close()
                         self.server_rcon_connection = None


                    if self.first_connection:
                         self.first_connection = False

                    #Reconnect (or connect if first time)
                    await self.manage_server_connection()
                    
                    #Start Tasks
                    self.start_rcon_messages_task()

                    continue

               #Connection active - Run pings every 10s to check the connection is still alive
               else:
                    #Ping or send a keep-alive message to the server to detect dropouts.
                    try:

                         await asyncio.wait_for(self.server_rcon_connection.ping(), timeout=10)

                    except Exception as e: #Bunch of random errors occur never the same one so safe to just use all 0.o

                         print(f"❌ : Failed to ping {self.nickname}. Error: {e}")

                         #Close the connection and let the reconnect logic handle it
                         await self.server_rcon_connection.close()
                         self.server_rcon_connection = None
       
                    
               #Check connection status every 10 seconds
               await asyncio.sleep(10)


     def start_connection_manager(self):
          """Start the connection manager in the background."""
          if not self.reconnect_task:
               self.reconnect_task = asyncio.create_task(self.maintain_connection())  # Run reconnection logic in background
          
          
     def start_rcon_messages_task(self):
          if not self.rcon_messages_task or self.rcon_messages_task.done():
               self.rcon_messages_task = asyncio.create_task(self.observe_all_rcon_messages())  #Actively scan for messages 

     

     async def run_a_raw_command(self, command: str,identifier, timeout: int = 10):
          """Run a raw command and wait for a response with the correct identifier."""
          if not self.server_rcon_connection or self.server_rcon_connection.closed:
               return None

          loop = asyncio.get_event_loop()
          response_future = loop.create_future()
          self.pending_responses[identifier] = response_future

          # Send the command with a unique identifier
          await self.server_rcon_connection.send_str(json.dumps({
               "Identifier": identifier,
               "Message": command,
               "Name": "FromDiscordRconBot"
          }))

          try:
               # Wait for the response or timeout
               return await asyncio.wait_for(response_future, timeout=timeout)
          except (aiohttp.ClientError, asyncio.TimeoutError) as e:
               #print(f"❌ : Failed to send command '{command}' to {self.ip}:{self.port}. Error: {e}")
               return None
          finally:
               # Cleanup in case of timeout or error
               self.pending_responses.pop(identifier, None)
          

     async def observe_all_rcon_messages(self):
          """Continuously listen for and handle incoming RCON messages."""
          
          while True:
               if self.server_rcon_connection and not self.server_rcon_connection.closed and self.server_session:
                    try:
                         #Up to 60s timeout
                         async for message in self.server_rcon_connection:
                              await asyncio.wait_for(self.process_rcon_messages(message), timeout=30)
                        

                    except asyncio.TimeoutError as e:
                         print(f"⚠️ : Timeout while listening to RCON messages.")
                         await asyncio.sleep(2) 

                    except Exception as e:
                    
                         print(f"⚠️ : Error while listening to RCON messages: {e}")
               

                         await asyncio.sleep(2) 
               
               await asyncio.sleep(5) #wait 5s hope connection comes back

     
     async def process_rcon_messages(self,message):
          #Process message, split f7's etc
          parsed_response = json.loads(message.data)

          #Handle single rcon messages
          if parsed_response["Identifier"] in self.pending_responses:
               self.pending_responses[parsed_response["Identifier"]].set_result(message.data)
               del self.pending_responses[parsed_response["Identifier"]]
               return 


