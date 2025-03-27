import json
import discord
import aiohttp
import asyncio
from datetime import datetime
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from RconManager import RconManager
import shared_resources
from Bots.GlobalPop import GlobalPop
from Bots.SinglePopBot import SinglePopBot
import multiprocessing

#Rcon connect to all the servers
async def start_rcon_connections_to_servers():
    for server in shared_resources.GEN_CONFIG["Servers"]:
        rcon_connect = RconManager(
            ip=server["ip"],
            port=server["rcon_port"],
            password=server["rcon_password"],
            nickname=server["name"]
        )

        print(f"Starting connection to {server['name']}")
        rcon_connect.start_connection_manager()
        shared_resources.Active_Rcon_Connections[server['name']] = rcon_connect
        print(f"Connection to {server['name']} established")



##Go through all the bots and start them

#Start a single bot
async def run_single_bot(token,name):
    bot = SinglePopBot(name)
    await bot.start(token)

#Start the global bot
async def run_global_bot(token):
    bot = GlobalPop()
    await bot.start(token)

#Run the bots



async def setup_all_bots():
    rcon_task = asyncio.create_task(start_rcon_connections_to_servers())

    tasks = [rcon_task]

    #Single Pop Bots
    for server in shared_resources.GEN_CONFIG["Servers"]:
        tasks.append(asyncio.create_task(run_single_bot(server['discord_bot_token'], server['name'])))


    #Global Pop Bot
    tasks.append(asyncio.create_task(run_global_bot(shared_resources.GEN_CONFIG['GlobalBotDiscordToken'])))


    # Keep the main process alive while subprocesses run
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(setup_all_bots())



