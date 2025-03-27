
# Examples of it setup!
![Example](https://i.imgur.com/EYj2j55.png)
![Example](https://i.imgur.com/g5aDuG6.png)

# Rust Multi Discord Pop Bot Script
Simple script to manage multiple pop bots and a global one for rust game servers in discord

NB : If your not using a bot container :
You will need to install python and git (must be 3.7+)
(https://www.youtube.com/watch?v=XF_rklW9XkU&ab_channel=CBTNuggets)

1. Go to https://discord.com/developers/applications, create a new bot application

2. Go to O2Auth - > URL Generator -> Select bot & invite the bot to your discord

3. Go to BOT -> reset token -> input token in the config 

# Example Config
```
{   "RefreshRate":10,
    "GlobalBotDiscordToken":"",

    "Servers":[
        {
            "name":"server_name_1",
            "ip":"168.100.161.191",
            "rcon_port":28065,
            "rcon_password":"",
            "discord_bot_token":""
        },
        {
            "name":"server_name_2",
            "ip":"168.100.161.191",
            "rcon_port":28085,
            "rcon_password":"",
            "discord_bot_token":""
        }
    ]
}
```

5. Input your rust game info, serverip, rcon port and password

6. Install requirements run **pip install -r requirements.txt** in your console

7. Run the main.py file to run the script 

**NB - The server names must be unique for the script to work**

Suggested hosts -> https://serverstarter.host/ or anything offering a simple bot container - Python is key!


