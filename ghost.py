import certifi
import os
os.environ["SSL_CERT_FILE"] = certifi.where()

import sys
import requests
import time
import discord
import faker
import random
import asyncio
import colorama
import base64
import threading
import json
import string
import logging

headless = False
try:
    import ttkbootstrap
except ModuleNotFoundError:
    headless = True

from discord.errors import LoginFailure
from discord.ext import commands

from pypresence import Presence
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from utils import console
from utils import config
from utils import notifier
from utils import scripts
from utils import files
from utils import codeblock
from utils import cmdhelper
from utils import imgembed
from utils import sessionspoof
if not headless: from utils import gui as ghost_gui

# import utils as ghost_utils
import commands as ghost_commands
import events as ghost_events

if discord.__version__ < "2.0.0":
    for _ in range(100):
        console.print_error("Ghost only supports discord.py-self 2.0.0, please upgrade!")

    sys.exit()

config.MAKE_CONFIG()
cfg = config.Config()
cfg.check()
token = cfg.get("token")
files.create_defaults()

session_spoofing, session_spoofing_device = cfg.get_session_spoofing()

if session_spoofing:
    sessionspoof.patch_identify(session_spoofing_device)

status_resp = requests.get("https://discord.com/api/users/@me/settings", headers={"Authorization": cfg.get("token")})
status = "online" if status_resp.status_code != 200 else status_resp.json()["status"]

ghost = commands.Bot(
    command_prefix=cfg.get("prefix"),
    self_bot=True,
    help_command=None,
    status=discord.Status.try_value(status)
)

if not headless: gui = ghost_gui.GhostGUI(ghost)
user = requests.get("https://discord.com/api/users/@me", headers={"Authorization": cfg.get("token")}).json()
rpc_log = ""
presence = cfg.get_rich_presence()

if presence.enabled:
    try:
        rpc = Presence(int(presence.client_id))
        rpc.connect()
        rpc.update(**presence.to_dict())
    
        rpc_log = "Rich Presence connected succesfully!"
    except Exception as e:
        rpc_log = e

for script_file in os.listdir("scripts"):
    if script_file.endswith(".py"):
        scripts.add_script("scripts/" + script_file, globals(), locals())

@ghost.event
async def on_connect():
    if not headless: gui.bot_started = True
    ghost.start_time = time.time()

    await ghost.add_cog(ghost_commands.Account(ghost))
    await ghost.add_cog(ghost_commands.Fun(ghost))
    await ghost.add_cog(ghost_commands.General(ghost))
    await ghost.add_cog(ghost_commands.Img(ghost))
    await ghost.add_cog(ghost_commands.Info(ghost))
    await ghost.add_cog(ghost_commands.Mod(ghost))
    await ghost.add_cog(ghost_commands.Nsfw(ghost))
    await ghost.add_cog(ghost_commands.Text(ghost))
    await ghost.add_cog(ghost_commands.Theming(ghost))
    await ghost.add_cog(ghost_commands.Util(ghost))
    await ghost.add_cog(ghost_commands.Abuse(ghost))
    await ghost.add_cog(ghost_commands.Sniper(ghost))
    await ghost.add_cog(ghost_events.NitroSniper(ghost))
    await ghost.add_cog(ghost_events.PrivnoteSniper(ghost))

    if sys.platform in ["darwin", "linux"]:
        os.environ["PYTHONWARNINGS"] = "ignore:IMKClient_Legacy"
        os.environ["PYTHONWARNINGS"] = "ignore:IMKInputSession_Legacy"

    text = f"Logged in as {ghost.user.name}"
    if str(ghost.user.discriminator) != "0":
        text += f"#{ghost.user.discriminator}"

    console.clear()
    console.resize(columns=90, rows=25)
    console.print_banner()
    console.print_info(text)
    console.print_info(f"You can now use commands with {cfg.get('prefix')}")
    print()

    if cfg.get_rich_presence().enabled:
        console.print_rpc(rpc_log)

    if session_spoofing:
        console.print_info(f"Spoofing session as {session_spoofing_device}")

    if cfg.get("message_settings")["style"] == "embed" and cfg.get("rich_embed_webhook") == "":
        console.print_error("Rich embed webhook not set! Using codeblock mode instead.")

    notifier.Notifier.send("Ghost", text)

@ghost.event
async def on_command(ctx):
    try:
        await ctx.message.delete()
    except Exception as e:
        console.print_error(str(e))

    command = ctx.message.content[len(ghost.command_prefix):]
    console.print_cmd(command)
    cfg.add_command_history(command)

@ghost.event
async def on_command_error(ctx, error):
    try:
        await ctx.message.delete()
    except Exception as e:
        console.print_error(str(e))

    try:
        await cmdhelper.send_message(ctx, {
            "title": "Error",
            "description": str(error),
            "colour": "#ff0000"
        })

    except Exception as e:
        console.print_error(f"{e}")

    console.print_error(str(error))

while token == "":
    console.print_error("Invalid token, please set a new one below.")
    new_token = input("> ")
    cfg.set("token", new_token)
    cfg.save()

try:
    if not headless:
        gui.run()
    else:
        ghost.run(token, log_handler=console.handler)
except Exception as e:
    console.print_error(str(e))
