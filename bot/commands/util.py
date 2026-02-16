import os
import sys
import discord
import json
import time
import psutil
import platform
import asyncio

from discord.ext import commands
from utils import config
from utils import console
from utils import files
import bot.helpers.cmdhelper as cmdhelper
import bot.helpers.codeblock as codeblock

class Util(commands.Cog):
    def __init__(self, bot, bot_controller):
        self.bot = bot
        self.description = cmdhelper.cog_desc("util", "Utility commands")
        self.cfg = config.Config()
        self.bot_controller = bot_controller

    @commands.command(name="util", description="Utility commands.", aliases=["utilities", "utility", "utils"], usage="")
    async def util(self, ctx, selected_page: int = 1):
        cfg = self.cfg
        pages = cmdhelper.generate_help_pages(self.bot, "Util")

        await cmdhelper.send_message(ctx, {
            "title": f"🧰 utility commands",
            "description": pages[cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.group(name="config", description="Configure ghost.", usage="", aliases=["cfg"])
    async def config(self, ctx):
        cfg = self.cfg

        if ctx.invoked_subcommand is None:
            sanitized_cfg = cfg.config.copy()
            sanitized_cfg.pop("token")
            sanitized_cfg["apis"] = {key: "******" for key in sanitized_cfg.get("apis", {})}

            def redact_webhooks(d):
                for key, value in d.items():
                    if isinstance(value, dict):
                        redact_webhooks(value)
                    if "webhook" in key:
                        d[key] = "******"

            redact_webhooks(sanitized_cfg)

            key_priority = {"prefix": 0, "theme": 1, "gui": 2, "rich_presence": 3}
            key_priority.update({key: idx + 4 for idx, key in enumerate(sanitized_cfg) if key not in key_priority})

            sorted_cfg = dict(sorted(sanitized_cfg.items(), key=lambda item: key_priority.get(item[0], float('inf'))))
            formatted_cfg = "\n".join(line[4:] for line in json.dumps(sorted_cfg, indent=4)[1:-1].split("\n"))

            await ctx.send(str(codeblock.Codeblock(
                title="config",
                description=formatted_cfg,
                style="json",
                footer="use 'config set [key] [value]' to edit a value",
                extra_title="sensitive data has been redacted"
            )), delete_after=cfg.get("message_settings")["auto_delete_delay"])

    @config.command(name="set", description="Set a config value.", usage="[key] [value]")
    async def set(self, ctx, key, *, value):
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False

        if key.lower() == "message_settings.auto_delete_delay":
            try:
                value = int(value)
            except ValueError:
                await ctx.send(str(codeblock.Codeblock(title="error", extra_title="the value isnt an integer")), delete_after=self.cfg.get("message_settings")["auto_delete_delay"])
                return

        if "." in key:
            key2 = key.split(".")
            if key2[0] not in self.cfg.config or key2[1] not in self.cfg.config[key2[0]]:
                await ctx.send(str(codeblock.Codeblock(title="error", extra_title="invalid key")), delete_after=self.cfg.get("message_settings")["auto_delete_delay"])
                return

        else:
            if key not in self.cfg.config:
                await ctx.send(str(codeblock.Codeblock(title="error", extra_title="invalid key")), delete_after=self.cfg.get("message_settings")["auto_delete_delay"])
                return

        if key == "prefix":
            self.bot.command_prefix = value

        if "." in key:
            key2 = key.split(".")
            self.cfg.config[key2[0]][key2[1]] = value

        else:
            self.cfg.config[key] = value

        self.cfg.save()
        await ctx.send(str(codeblock.Codeblock(title="config", extra_title="key updated", description=f"{key} :: {value}")), delete_after=self.cfg.get("message_settings")["auto_delete_delay"])

    @commands.command(name="restart", description="Restart the bot.", usage="", aliases=["reboot", "reload"])
    async def restart(self, ctx, no_response=False):
        cfg = self.cfg

        if not no_response:
            await cmdhelper.send_message(ctx, {
                "title": cfg.theme.title,
                "description": "restarting ghost..." if cfg.get("message_settings")["style"] == "image" else ""
            }, extra_title="restarting ghost...")

        if self.bot_controller.gui:
            self.bot_controller.restart_gui()
        else:
            os.execl(sys.executable, sys.executable, *sys.argv)

    @commands.command(name="quit", description="Quit the bot.", usage="", aliases=["exit"])
    async def quit(self, ctx, output=True):
        cfg = self.cfg

        if output:
            await cmdhelper.send_message(ctx, {
                "title": cfg.theme.title,
                "description": "quitting ghost..." if cfg.get("message_settings")["style"] == "image" else ""
            }, extra_title="quitting ghost...")

        sys.exit()

    @commands.command(name="settings", description="View ghost's settings.", usage="")
    async def settings(self, ctx):
        cfg = self.cfg
        command_amount = len(self.bot.commands)
        uptime = time.time() - self.bot.start_time
        uptime = cmdhelper.format_time(uptime)

        info = {
            "Prefix": cfg.get("prefix"),
            "Rich Presence": cfg.get("rich_presence"),
            "Theme": cfg.theme.name,
            "Style": cfg.get("message_settings")["style"],
            "Uptime": uptime,
            "Command Amount": command_amount,
        }

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "Settings",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()]),
            "thumbnail": ""
        })

    @commands.command(name="prefix", description="Set the prefix", usage="[prefix]")
    async def prefix(self, ctx, prefix):
        cfg = self.cfg
        if self.bot.command_prefix == prefix:
            await cmdhelper.send_message(ctx, discord.Embed(title="prefix", description=f"{prefix} is already youre prefix").to_dict())
        else:
            await cmdhelper.send_message(ctx, discord.Embed(title="prefix", description=f"Set your prefix to {prefix}").to_dict())
            self.bot.command_prefix = prefix
            cfg.set("prefix", prefix)

    @commands.command(name="clearcache", description="Clear the cache", usage="")
    async def clearcache(self, ctx):
        if not os.listdir("data/cache"):
            await cmdhelper.send_message(ctx, {
                "title": "Cache",
                "description": "Cache is already empty",
            })
            return

        for file in os.listdir("data/cache"):
            os.remove(f"data/cache/{file}")

        await cmdhelper.send_message(ctx, {
            "title": "Cache",
            "description": "Cache cleared!",
        })

    # @commands.command(name="gui", description="Enable the GUI", usage="", aliases=["enablegui"])
    # async def gui(self, ctx):
    #     cfg = config.Config()
    #     cfg.set("gui", True)
    #     cfg.save()

    #     await cmdhelper.send_message(ctx, {
    #         "title": "GUI",
    #         "description": "GUI is now enabled\nRestarting to apply changes...",
    #         "colour": "#00ff00"
    #     })

    #     await self.restart(ctx, no_response=True)

    @commands.command(name="richpresence", description="Toggle rich presence", usage="", aliases=["rpc"])
    async def richpresence(self, ctx):
        cfg = self.cfg
        rpc = cfg.get_rich_presence()
        rpc.enabled = not rpc.enabled
        rpc.save()

        await cmdhelper.send_message(ctx, {
            "title": "Rich Presence",
            "description": f"Rich Presence is now {'enabled' if rpc.enabled else 'disabled'}\nRestarting to apply changes...",
            "colour": "#00ff00" if rpc.enabled else "#ff0000"
        })

        await self.restart(ctx, no_response=True)

    @commands.command(name="resetrichpresence", description="Reset rich presences to defaults.", usage="", aliases=["resetrpc", "rpcreset"])
    async def resetrichpresence(self, ctx):
        cfg = self.cfg
        rpc = cfg.get_rich_presence()
        rpc.reset_defaults()

        await cmdhelper.send_message(ctx, {
            "title": "Rich Presence",
            "description": "Rich presence has now been reset to defaults.\nRestarting to apply changes..."
            })

        await self.restart(ctx, no_response=True)

    @commands.command(name="specs", description="View your computer's specs", usage="")
    async def specs(self, ctx):
        os_logos = {
            "windows": "https://benny.fun/static/os-logos/windows.jpg",
            "darwin": "https://benny.fun/static/os-logos/apple.jpg",
            "linux": "https://benny.fun/static/os-logos/tux.jpg"
        }
        cpu_name = platform.processor()
        used_ram_size = psutil.virtual_memory().used
        ram_size = psutil.virtual_memory().total
        os_name = platform.system()
        disk_size = psutil.disk_usage("C:").total if os_name == "Windows" else psutil.disk_usage("/").total
        python_version = platform.python_version()

        used_ram_size = f"{used_ram_size // 1000000000}GB"
        ram_size = f"{ram_size // 1000000000}GB"
        disk_size = f"{disk_size // 1000000000}GB"

        info = {
            "OS": f"{os_name}",
            "Host": f"{platform.node()}",
            "Uptime": cmdhelper.format_time(time.time() - psutil.boot_time(), short_form=False),
            "CPU": cpu_name if cpu_name else "Unknown",
            "Memory": f"{used_ram_size}/{ram_size}",
            "Disk": f"{disk_size}",
            "Python": python_version,
        }

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "Computer Specs",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()]),
            "thumbnail": os_logos[os_name.lower()]
        })

    @commands.command(name="sessionspoofer", description="Spoof your session", usage="[device]", aliases=["sessionspoof", "spoofsession"])
    async def sessionspoofer(self, ctx, device = None):
        cfg = self.cfg
        devices = ["mobile", "desktop", "web", "embedded"]
        spoofing, spoofing_device = cfg.get_session_spoofing()

        if not spoofing:
            await cmdhelper.send_message(ctx, {
                "title": "Session Spoofing",
                "description": "Session spoofing is not enabled. Enable it in the config.",
                "colour": "#ff0000"
            })
            return

        if device not in devices:
            await cmdhelper.send_message(ctx, {
                "title": "Session Spoofing",
                "description": f"Invalid device. Options: {', '.join(devices)}",
                "colour": "#ff0000"
            })
            return

        if device is None:
            cfg.set_session_spoofing(not spoofing, spoofing_device)

            await cmdhelper.send_message(ctx, {
                "title": "Session Spoofing",
                "description": f"Session spoofing is now {'enabled' if not spoofing else 'disabled'}\nRestarting to apply changes...",
                "colour": "#00ff00" if not spoofing else "#ff0000"
            })

        else:
            cfg.set_session_spoofing(spoofing, device)

            await cmdhelper.send_message(ctx, {
                "title": "Session Spoofing",
                "description": f"Session spoofing is now enabled as {device}\nRestarting to apply changes...",
                "colour": "#00ff00"
            })

        cfg.save()
        await self.restart(ctx, no_response=True)

    @commands.command(name="uptime", description="View the bot's uptime", usage="")
    async def uptime(self, ctx):
        uptime = time.time() - self.bot.start_time
        uptime = cmdhelper.format_time(uptime, short_form=False)

        await cmdhelper.send_message(ctx, {
            "title": "Uptime",
            "description": f"Ghost has been running for **{uptime}**"
        })

    @commands.command(name="allcmds", description="List all commands", usage="")
    async def allcmds(self, ctx):
        cfg = self.cfg
        commands = [f"{command.name} {command.usage} : {command.description}" for command in self.bot.commands]

        with open(files.get_application_support() + "/data/commands.txt", "w") as f:
            f.write("\n".join(commands))

        await ctx.send(file=discord.File(files.get_application_support() + "/data/commands.txt"), delete_after=cfg.get("message_settings")["auto_delete_delay"])

    @commands.command(name="clearconsole", description="Clear the console", usage="")
    async def clearconsole(self, ctx):
        console.clear()
        console.print_banner()

        await cmdhelper.send_message(ctx, {
            "title": "Console",
            "description": "Console cleared",
        })

    @commands.command(name="commandhistory", description="Get the history of commands used.", aliases=["cmdhistory"])
    async def commandhistory(self, ctx):
        cfg = self.cfg
        history = cfg.get_command_history()
        description = "\n".join([f"[{t}] {c}" for t, c in history])

        await ctx.send(codeblock.Codeblock(
            title="Command History",
            description=description
            ), delete_after=cfg.get("message_settings")["auto_delete_delay"])

    @commands.command(name="surveillance", description="Get a list of every message a member has sent in mutual servers.", usage="[member]")
    async def surveillance(self, ctx, member_id: int = None):
        await cmdhelper.send_message(ctx, {
            "title": "Surveillance",
            "description": "This is a GUI only feature, please open the GUI to use it.",
            "colour": "#ff0000"
        })
        return
        
    #     mutual_guilds = [guild for guild in self.bot.guilds if guild.get_member(member_id)]
    #     data = {}
    #     tasks = []
    #     sem = asyncio.Semaphore(10)
    #     stop_event = asyncio.Event()
    #     last_saved_count = 0

    #     def _count_messages():
    #         return sum(len(channels) for guilds in data.values() for channels in guilds.values())

    #     def _save_data():
    #         nonlocal last_saved_count
    #         current_count = _count_messages()
    #         if current_count == last_saved_count:
    #             return
    #         last_saved_count = current_count
            
    #         with open(files.get_application_support() + "/data/surveillance.json", "w") as f:
    #             json.dump(data, f, indent=4)
    #         console.print_info(f"Auto-saved {current_count} messages.")

    #     async def _autosave(interval=5):
    #         while not stop_event.is_set():
    #             await asyncio.sleep(interval)
    #             _save_data()
                
    #         console.print_info("Auto-saving stopped. Surveillance complete!")

    #     def _add_message(guild, channel, message):
    #         if guild.name not in data: data[guild.name] = {}
    #         if channel.name not in data[guild.name]: data[guild.name][channel.name] = []
            
    #         data[guild.name][channel.name].append(message)
    #         # _save_data()

    #     def _get_permissions(channel):
    #         member = channel.guild.get_member(member_id)
    #         member_role = member.top_role
    #         bot_role = channel.guild.me.top_role
        
    #         return (channel.permissions_for(member).read_messages and 
    #                 channel.permissions_for(channel.guild.me).read_messages or 
    #                 channel.overwrites_for(member_role).read_messages and 
    #                 channel.overwrites_for(bot_role).read_messages)
        

    #     async def _fetch_context_channel(channel):
    #         if channel.id == ctx.channel.id:
    #             return ctx.channel
    #         try:
    #             latest_msg = [msg async for msg in channel.history(limit=1)][0]
    #             context = await self.bot.get_context(latest_msg)
                
    #             console.success(f"Got context for {channel.guild.name} - {channel.name}")
                
    #             return context.channel
    #         except Exception as e:
    #             if "429" in str(e):
    #                 console.error(f"Rate limited while fetching context for {channel.guild.name} - {channel.name}")
    #                 await asyncio.sleep(5)
    #                 return await _fetch_context_channel(channel)
                
    #             return None

    #     async def _get_messages(channel, delay=0.25, oldest_first=False):
    #         async with sem:
    #             try:
    #                 await asyncio.sleep(delay)
    #                 console.print_info(f"Finding messages in {channel.guild.name} - {channel.name}")

    #                 channel = await _fetch_context_channel(channel) or channel
    #                 guild = channel.guild
    #                 messages = []

    #                 try:
    #                     async for msg in channel.history(limit=None, oldest_first=oldest_first):
    #                         print(channel.name, msg.author.id, msg.content)
    #                         if msg.author.id == member_id:
    #                             if len(msg.attachments) > 0:
    #                                 attachments = "\n".join([f"Attachment: {attachment.url}" for attachment in msg.attachments])
    #                                 msg_string = f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.content}\n{attachments}"
    #                             else:
    #                                 msg_string = f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.content}"
    #                             messages.append(msg_string)
    #                             _add_message(guild, channel, msg_string)
    #                             console.print_info(f"Found message in {channel.guild.name} - {channel.name}")
                                
    #                     if len(messages) > 0: 
    #                         console.print_success(f"Found messages in {channel.guild.name} - {channel.name}")
    #                     else:
    #                         console.print_error(f"Found no messages in {channel.guild.name} - {channel.name}")
    #                 except Exception as e:
    #                     if "429" in str(e).lower():
    #                         console.print_error("Rate limited! Waiting for 5 seconds...")
    #                         await asyncio.sleep(5)
    #                         return await _get_messages(channel, delay)
    #                     else:
    #                         console.print_error(f"Error in {channel.guild.name} - {channel.name}: {e}")
    #                         return

    #                 _save_data()
    #             except asyncio.CancelledError:
    #                 console.print_warning("Process was cancelled! Saving progress...")
    #                 stop_event.set()
    #                 _save_data()
    #                 raise
    #             except Exception as e:
    #                 console.print_error(f"Error in {channel.guild.name} - {channel.name}: {e}")
    #             finally:
    #                 _save_data()

    #     async def _attempt_scrape(guild, delay):
    #         tasks = []
    #         console.info(f"Attempting to scrape {guild.name} - {guild.id}")
            
    #         for channel in guild.channels:
    #             if isinstance(channel, discord.TextChannel) and _get_permissions(channel):
    #                 tasks.append(_get_messages(channel, delay, oldest_first=True))
    #                 delay += 2
                    
    #         if len(tasks) == 0:
    #             console.print_error(f"No valid channels in {guild.name} - {guild.id}")
    #             return
            
    #         try:
    #             await asyncio.gather(*tasks)
    #         except asyncio.CancelledError:
    #             console.print_warning("Process was cancelled! Saving progress...")
    #             stop_event.set()
    #             _save_data()
    #             raise

    #     delay = 1
    #     autosave_task = asyncio.create_task(_autosave(5))
        
    #     for guild in mutual_guilds:
    #         tasks.append(_attempt_scrape(guild, delay))
    #         delay += 1.5

    #     await asyncio.gather(*tasks)
    #     stop_event.set()
    #     await autosave_task
    #     _save_data()
        
    #     console.print_success("Spypet complete! Data saved to data/surveillance.json.")
    #     console.print_info(f"Total messages: {_count_messages()}")
    #     console.print_info(f"Total guilds: {len(data)}")
    #     console.print_info(f"Total channels: {sum(len(channels) for channels in data.values())}")
    #     await ctx.send(file=discord.File(files.get_application_support() + "/data/surveillance.json"), delete_after=self.cfg.get("message_settings")["auto_delete_delay"])

    @commands.command(name="latency", description="Check the bot's latency", usage="")
    async def latency(self, ctx):
        msg = await cmdhelper.send_message(ctx, {
            "title": "Latency",
            "description": "Calculating latency..."
        })
        
        latency = (msg.created_at - ctx.message.created_at).total_seconds() * 1000
        websocket_latency = self.bot.latency * 1000
        
        await msg.delete()
        
        await cmdhelper.send_message(ctx, {
            "title": "Latency",
            "description": f"Message latency: {round(latency)}ms\nWebSocket latency: {round(websocket_latency)}ms"
        })

def setup(bot):
    bot.add_cog(Util(bot))
