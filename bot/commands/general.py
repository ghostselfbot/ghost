import requests

from discord.ext import commands
from utils import config
import bot.helpers.cmdhelper as cmdhelper
import bot.helpers.codeblock as codeblock

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = cmdhelper.cog_desc("help", "Get help with a command")
        self.cfg = config.Config()

    @commands.command(name="help", description="A list of all categories.", usage="")
    async def help(self, ctx, command: str = None, shared: bool = False):
        cfg = self.cfg
        descriptions = {"codeblock": "", "image": "", "embed": ""}
        cmds = []
        cogs = self.bot.cogs
        
        if shared:
            cogs = {cog_name: cog for cog_name, cog in cogs.items() if cog_name.lower() in self.bot.allowed_cogs}

        for _, cog in cogs.items():
            if cog.description:
                parts = cog.description.split("\n")
                if len(parts) > 1:
                    cmds.append({"name": parts[1].lower(), "description": parts[0]})

        # cmds.sort(key=lambda k: len(k["description"]), reverse=False) 
        # sort the cmds by the name in alphabetical order
        cmds.sort(key=lambda k: k["name"], reverse=False)
        max_name_length = max((len(cmd["name"]) for cmd in cmds if cmd["name"] != "help"), default=0)

        for cmd in cmds:
            if cmd["name"] == "help":
                continue
            spacing = " " * (max_name_length - len(cmd["name"]))
            descriptions["codeblock"] += f"{spacing}{cmd['name']} :: {cmd['description']}\n"
            descriptions["image"] += f"{self.bot.command_prefix}**{cmd['name']}** {cmd['description']}\n"
            descriptions["embed"] += f"{self.bot.command_prefix}{cmd['name']} ~ {cmd['description']}\n"

        if command is None:
            await cmdhelper.send_message(ctx, {
                "title": cfg.theme.title,
                "description": f"{descriptions['image'] if cfg.get('message_settings')['style'] == 'image' else descriptions['embed']}\nThere are **{len(self.bot.commands)}** commands!",
                "codeblock_desc": descriptions["codeblock"]
            }, extra_title=f"{len(self.bot.commands)} total commands")
        else:
            cmd_obj = self.bot.get_command(command)
            if not cmd_obj:
                await cmdhelper.send_error_message(ctx, f"Command **{command}** not found.")
                return

            info = {"name": cmd_obj.name, "description": cmd_obj.description, "usage": cmd_obj.usage}
            max_key_length = max(len(key) for key in info)

            description_text = "\n".join([f"**{key}:** {value}" for key, value in info.items()])
            codeblock_text = "\n".join([f"{key}{' ' * (max_key_length - len(key))} :: {value}" for key, value in info.items()])

            await cmdhelper.send_message(ctx, {
                "title": "Help",
                "description": description_text,
                "codeblock_desc": codeblock_text
            })

    @commands.command()
    async def ping(self, ctx):
        cfg = self.cfg
        latency = requests.get("https://discord.com/api/users/@me", headers={"Authorization": cfg.get("token")}).elapsed.total_seconds()
        msg = codeblock.Codeblock(f"ping", extra_title=f"Your latency is {round(latency * 1000)}ms")

        await ctx.send(msg, delete_after=cfg.get("message_settings")["auto_delete_delay"])
    
    @commands.command(name="search", description="Search for commands.", usage="[query]")
    async def search(self, ctx, query: str, selected_page: int = 1):
        cfg = self.cfg
        commands = self.bot.walk_commands()
        commands_formatted = []
        commands_2 = []
        spacing = 0
        pages = []
        
        def search_aliases(command, query):
            for alias in command.aliases:
                if query in alias:
                    return True

            return False

        for cmd in commands:
            if query in cmd.name or query in cmd.description or search_aliases(cmd, query):
                prefix = cmdhelper.get_command_full_name(cmd)

                if len(prefix) > spacing:
                    spacing = len(prefix)

                commands_2.append([prefix, cmd.description])

        for cmd in commands_2:
            if cfg.get("message_settings")["style"] == "codeblock":
                commands_formatted.append(f"{cmd[0]}{' ' * (spacing - len(cmd[0]))} :: {cmd[1]}")
            else:
                commands_formatted.append(f"**{cmd[0]}** {cmd[1]}")

        commands_str = ""
        for cmd in commands_formatted:
            if len(commands_str) + len(cmd) > 1000:
                pages.append(commands_str)
                commands_str = ""

            commands_str += f"{cmd}\n"

        if len(commands_str) > 0:
            pages.append(commands_str)
        
        if len(pages) == 0:
            await cmdhelper.send_message(ctx, {
                "title": "Search",
                "description": f"No results found for **{query}**.",
                "colour": "#ff0000"
            })

        else:
            await cmdhelper.send_message(ctx, {
                "title": "Search",
                "description": pages[selected_page - 1],
                "codeblock_desc": pages[selected_page - 1],
                "footer": f"Page {selected_page}/{len(pages)}"
            }, extra_title=f"Page {selected_page}/{len(pages)}")

    # @commands.command(name="scripts", description="List all scripts.", usage="")
    # async def scripts_cmd(self, ctx, selected_page: int = 1):
    #     cfg = self.cfg
    #     scripts_list = scripts.get_scripts()

    #     if len(scripts_list) == 0:
    #         await cmdhelper.send_message(ctx, {
    #             "title": "Scripts",
    #             "description": "No scripts found.",
    #             "colour": "#ff0000"
    #         })

    #     else:
    #         pages = []
    #         scripts_str = ""
    #         for script in scripts_list:
    #             if len(scripts_str) + len(script) > 1000:
    #                 pages.append(scripts_str)
    #                 scripts_str = ""

    #             script_in_cmds = False
    #             script_name = script.split("/")[-1].replace(".py", "")

    #             for cmd in self.bot.commands:
    #                 if cmd.name == script_name:
    #                     script_in_cmds = True
    #                     break

    #             if script_in_cmds:
    #                     if cfg.get("message_settings")["style"] == "codeblock":
    #                         scripts_str += f"{cmd.name} :: {cmd.description}\n"
    #                     else:
    #                         scripts_str += f"**{self.bot.command_prefix}{cmd.name}** {cmd.description}\n" 
    #             else:
    #                 if cfg.get("message_settings")["style"] == "codeblock":
    #                     scripts_str += f"{script_name} :: Script name not found as a command\n"
    #                 else:
    #                     scripts_str += f"**{script_name}** Script name not found as a command\n" 

    #         if len(scripts_str) > 0:
    #             pages.append(scripts_str)

    #         await cmdhelper.send_message(ctx, {
    #             "title": "Scripts",
    #             "description": pages[selected_page - 1],
    #             "codeblock_desc": pages[selected_page - 1],
    #             "footer": f"Page {selected_page}/{len(pages)}"
    #         }, extra_title=f"Page {selected_page}/{len(pages)}")

def setup(bot):
    bot.add_cog(General(bot))