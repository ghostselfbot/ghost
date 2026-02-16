import discord
import time
import random
import certifi
import os
import asyncio
import inspect
import importlib.util
import sys

os.environ["SSL_CERT_FILE"] = certifi.where()
from discord.ext import commands, tasks

from utils import files
from utils.config import Config
import utils.console as console

import bot.helpers.sessionspoof as sessionspoof
import bot.helpers.cmdhelper as cmdhelper
from bot.helpers import get_external_asset, generate_activity_json

import bot.commands as ghost_commands
import bot.events as ghost_events

import asyncio
import random

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

class Ghost(commands.Bot):
    def __init__(self, controller):
        self.cfg = Config()
        self.controller = controller
        self.session_spoofing, self.session_spoofing_device = self.cfg.get_session_spoofing()

        if self.session_spoofing:
            sessionspoof.patch_identify(self.session_spoofing_device)

        super().__init__(command_prefix=self.cfg.get("prefix"), self_bot=True, help_command=None)
        self.start_time = None
        self.files = files
                
    async def _setup_scripts(self):
        scripts = self.cfg.get_scripts()

        for script in scripts:
            script_name = script.replace(".py", "")
            script_path = files.get_application_support() + f"/scripts/{script}"

            try:
                script_globals = {
                    'discord': discord,
                    'commands': commands,
                    'console': console,
                    'cmdhelper': cmdhelper,
                    'asyncio': asyncio,
                    'time': time,
                    'tasks': tasks,
                    'random': random,
                    'os': os,
                    '_ghost_config': self.cfg,
                    '_ghost_session_spoofer': sessionspoof,
                    '_ghost_bot_controller': self.controller,
                    'files': self.files,
                    '_themes_path': files.get_themes_path,
                    'command': self.command,
                    'event': self.event,
                    'ghost': self
                }
                
                # Execute script
                with open(script_path, 'r') as f:
                    script_code = f.read()
                
                exec(script_code, script_globals)
                
                # Collect commands and events from the script
                script_commands = []
                script_events = {}
                
                for name, obj in script_globals.items():
                    if isinstance(obj, commands.Command):
                        script_commands.append(obj)
                    elif callable(obj) and name.startswith('on_'):
                        script_events[name] = obj
                
                # Create dynamic cog class
                def create_script_cog(script_name, script_commands, script_events, bot):
                    # Create a unique class name using the script name
                    cog_class_name = f'{script_name.capitalize()}ScriptCog'

                    class ScriptCog(commands.Cog, name=cog_class_name):
                        def __init__(self, bot):
                            self.bot = bot
                            
                            # Add commands
                            for cmd in script_commands:
                                setattr(self, cmd.name, cmd.callback)
                            
                            # Store event functions but don't add them as listeners here
                            self.script_events = script_events
                        
                        # Add on_message as a proper cog listener if it exists
                        if 'on_message' in script_events:
                            @commands.Cog.listener()
                            async def on_message(self, message):
                                await self.bot.process_commands(message)
                                await script_events['on_message'](message)
                            
                            # Add the method to the class
                            self.on_message = on_message
                                        
                    ScriptCog.__name__ = f'{script_name}Cog'
                    ScriptCog.__module__ = f'scripts.{script_name}'
                    ScriptCog.__qualname__ = cog_class_name
                    return ScriptCog

                # Replace your dynamic cog creation with:
                ScriptCog = create_script_cog(script_name, script_commands, script_events, self)

                # Add the cog
                await self.add_cog(ScriptCog(self))
                
                console.print_info(f"Loaded script: {script_name}")
                self.controller.add_startup_script(script)

            except Exception as e:
                console.print_error(f"Error loading script: {script_name} - {e}")

    async def on_ready(self):
        try:
            self.start_time = time.time()
            self.cfg.add_token(self.cfg.get("token"), self.user.name, self.user.id)
            await self.load_cogs()

            text = f"Logged in as {self.user.name}"
            if str(self.user.discriminator) != "0":
                text += f"#{self.user.discriminator}"
            
            try:
                console.clear()
                console.resize(columns=90, rows=25)
                console.print_banner()
            except:
                pass
            
            self.controller.bot_running = True
            console.print_info(text)
            console.print_info(f"You can now use commands with {self.cfg.get('prefix')}")
            print()

            if self.session_spoofing:
                console.success(f"Spoofing session as {self.session_spoofing_device}")
                # console.print_warning("Your account is at higher risk of termination by using session spoofer.")
            
            await self._setup_scripts()
            await self.controller.setup_webhooks()
            self.controller.surveillance.set_bot(self)
            
        except Exception as e:
            console.print_error(str(e))

        cfg_rpc = self.cfg.get_rich_presence()
        if cfg_rpc.enabled:
            external_assets = {
                "large_image": await get_external_asset(self, cfg_rpc.large_image) if cfg_rpc.large_image else None,
                "small_image": await get_external_asset(self, cfg_rpc.small_image) if cfg_rpc.small_image else None
            }
            
            await self.ws.send_as_json({
                "op": 3,
                "d": {
                    "since": int(time.time() * 1000),
                    "activities": [generate_activity_json(external_assets)],
                    "status": "online",
                    "afk": True
                }
            })
            
            console.success("Rich Presence enabled")
        
    async def load_cogs(self):
        cogs = [
            ghost_commands.Account, ghost_commands.Fun, ghost_commands.General, ghost_commands.Img,
            ghost_commands.Info, ghost_commands.Mod, ghost_commands.Nsfw, ghost_commands.Text,
            ghost_commands.Theming, ghost_commands.Util, ghost_commands.Abuse, ghost_commands.Sniper,
            ghost_events.NitroSniper, ghost_events.PrivnoteSniper
        ]

        for cog in cogs:
            if cog == ghost_commands.Util or cog == ghost_commands.Sniper:
                await self.add_cog(cog(self, self.controller))
            else:
                await self.add_cog(cog(self))

    async def on_command(self, ctx):
        if self.cfg.get("message_settings")["style"] != "edited":
            try:
                await ctx.message.delete()
            except Exception as e:
                console.print_error(str(e))

        command = ctx.message.content[len(self.command_prefix):]
        console.print_cmd(command)
        self.cfg.add_command_history(command)

    async def on_command_error(self, ctx, error):
        console.print_error(str(error))

        if self.cfg.get("message_settings")["style"] != "edited":
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
            
    async def on_message_delete(self, message):
        if message.author.id == self.user.id:
            return
        delete_time = time.time()
        if self.controller.gui and hasattr(self.controller.gui, 'tools_page'):
            self.controller.gui.tools_page.message_logger_page.add_discord_log(message.author, message, delete_time)

    def run_bot(self):
        try:
            console.clear()
            console.print_info("Starting Ghost...")
            # self.run(self.cfg.get("token"), log_handler=console.handler)
            self.run(self.cfg.get("token"), log_handler=None)
        except Exception as e:
            console.print_error(str(e))
            exit(1)


if __name__ == "__main__":
    bot = Ghost()
    bot.run_bot()
