import os
import sys
import discord
import json
import time
import psutil
import platform

from discord.ext import commands
from utils import config
from utils import codeblock
from utils import cmdhelper
from utils import imgembed
from utils import console

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = cmdhelper.cog_desc("util", "Utility commands")
        self.cfg = config.Config()

    @commands.command(name="util", description="Utility commands.", aliases=["utilities", "utility", "utils"], usage="")
    async def util(self, ctx, selected_page: int = 1):
        cfg = config.Config()
        pages = cmdhelper.generate_help_pages(self.bot, "Util")

        await cmdhelper.send_message(ctx, {
            "title": f"🧰 utility commands",
            "description": pages[cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.group(name="config", description="Configure ghost.", usage="", aliases=["cfg"])
    async def config(self, ctx):
        cfg = config.Config()

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
    async def restart(self, ctx):
        cfg = config.Config()
        
        await cmdhelper.send_message(ctx, {
            "title": cfg.theme.title,
            "description": "restarting ghost..." if cfg.get("message_settings")["style"] == "image" else ""
        }, extra_title="restarting ghost...")
        
        os.execl(sys.executable, sys.executable, *sys.argv)

    @commands.command(name="quit", description="Quit the bot.", usage="", aliases=["exit"])
    async def quit(self, ctx, output=True):
        cfg = config.Config()

        if output:
            await cmdhelper.send_message(ctx, {
                "title": cfg.theme.title,
                "description": "quitting ghost..." if cfg.get("message_settings")["style"] == "image" else ""
            }, extra_title="quitting ghost...")

        sys.exit()

    @commands.command(name="settings", description="View ghost's settings.", usage="")
    async def settings(self, ctx):
        cfg = config.Config()
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
        cfg = config.Config()
        if self.bot.command_prefix == prefix:
            await cmdhelper.send_message(ctx, discord.Embed(title="prefix", description=f"{prefix} is already youre prefix").to_dict())
        else:
            await cmdhelper.send_message(ctx, discord.Embed(title="prefix", description=f"Set your prefix to {prefix}").to_dict())
            self.bot.command_prefix = prefix
            cfg.set("prefix", prefix)

    @commands.command(name="gui", description="Enable the GUI", usage="", aliases=["enablegui"])
    async def gui(self, ctx):
        cfg = config.Config()
        cfg.set("gui", True)
        cfg.save()

        await cmdhelper.send_message(ctx, {
            "title": "GUI",
            "description": "GUI is now enabled\nRestarting to apply changes...",
            "colour": "#00ff00"
        })

        await self.restart(ctx)

    @commands.command(name="richpresence", description="Toggle rich presence", usage="", aliases=["rpc"])
    async def richpresence(self, ctx):
        cfg = config.Config()
        rpc = cfg.get("rich_presence")

        cfg.set("rich_presence", not rpc)
        cfg.save()

        await cmdhelper.send_message(ctx, {
            "title": "Rich Presence",
            "description": f"Rich Presence is now {'enabled' if not rpc else 'disabled'}\nRestarting to apply changes...",
            "colour": "#00ff00" if not rpc else "#ff0000"
        })

        await self.restart(ctx)
        
    @commands.command(name="specs", description="View your computer's specs", usage="")
    async def specs(self, ctx):
        cpu_name = platform.processor()
        ram_size = psutil.virtual_memory().total
        disk_size = psutil.disk_usage("/").total
        os_name = platform.system()
        python_version = platform.python_version()

        if platform.system() == "Windows":
            disk_size = psutil.disk_usage("C:").total

        ram_size = f"{ram_size // 1000000000}GB"
        disk_size = f"{disk_size // 1000000000}GB"

        info = {
            "OS": f"{os_name}",
            "CPU": cpu_name if cpu_name else "Unknown",
            "RAM": f"{ram_size}",
            "Disk": f"{disk_size}",
            "Python": python_version,
        }

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "Computer Specs",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()]),
            "thumbnail": ""
        })

    @commands.command(name="sessionspoofer", description="Spoof your session", usage="[device]", aliases=["sessionspoof", "spoofsession"])
    async def sessionspoofer(self, ctx, device = None):
        cfg = config.Config()
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
        await self.restart(ctx)

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
        cfg = config.Config()
        commands = [f"{command.name} {command.usage} : {command.description}" for command in self.bot.commands]

        with open("data/commands.txt", "w") as f:
            f.write("\n".join(commands))

        await ctx.send(file=discord.File("data/commands.txt"), delete_after=cfg.get("message_settings")["auto_delete_delay"])

    @commands.command(name="clearconsole", description="Clear the console", usage="")
    async def clearconsole(self, ctx):
        console.clear()
        console.print_banner()

        await cmdhelper.send_message(ctx, {
            "title": "Console",
            "description": "Console cleared",
        })

def setup(bot):
    bot.add_cog(Util(bot))