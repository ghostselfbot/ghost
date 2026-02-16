import discord

from discord.ext import commands
from utils import config
import bot.helpers.cmdhelper as cmdhelper

class Theming(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = cmdhelper.cog_desc("theming", "Theme commands")
        self.cfg = config.Config()

    @commands.command(name="theming", description="Theme commands.", aliases=["design"], usage="")
    async def theming(self, ctx, selected_page: int = 1):
        cfg = self.cfg
        pages = cmdhelper.generate_help_pages(self.bot, "Theming")

        await cmdhelper.send_message(ctx, {
            "title": f"🎨 theme commands",
            "description": pages[cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.command(name="themes", description="Lists all your themes.", usage="[page]")
    async def themes(self, ctx, page: int = 1):
        cfg = self.cfg
        desc = ""

        themes = cfg.get_themes()
        page_size = 10
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        for i, theme in enumerate(themes[start_index:end_index]):
            desc += f"- {theme}\n"

        await cmdhelper.send_message(ctx, {
            "title": f"🎨 Themes (Page {page}/{(len(themes) + page_size - 1) // page_size})",
            "description": desc,
            "colour": cfg.theme.colour,
            "footer": f"Use {self.bot.command_prefix}theme [name] to change your theme",
        })

    @commands.group(name="theme", description="Theme commands.", usage="")
    async def theme(self, ctx):
        cfg = self.cfg

        if ctx.invoked_subcommand is None:
            msg_split = ctx.message.content.split(" ")
            if len(msg_split) >= 2:
                await self.change_theme(ctx, msg_split[1])

            else:
                theme = cfg.theme
                await cmdhelper.send_message(ctx, {
                    "title": f"🎨 Theme",
                    "description": f"Current theme: {theme.name}",
                    "colour": theme.colour,
                    "footer": theme.footer,
                })

    @theme.command(name="create", description="Create a new theme.", usage="[name]", aliases=["new", "add"])
    async def create_theme(self, ctx, theme_name: str = None):
        cfg = self.cfg
        description = ""
        colour = cfg.theme.colour

        if theme_name is None:
            description = "You need to provide a theme name!"
            colour = "#ff0000"
        elif cfg.theme_exists(theme_name):
            description = f"A theme named {theme_name} already exists!"
            colour = "#ff0000"
        else:
            cfg.create_theme(theme_name)
            description = f"Theme {theme_name} created!"

        await cmdhelper.send_message(ctx, {
            "title": f"🎨 Theme",
            "description": description,
            "colour": colour,
            "footer": cfg.theme.footer,
        })
        
    @theme.command(name="delete", description="Delete a theme.", usage="[name]", aliases=["remove", "del", "rm"])
    async def delete_theme(self, ctx, theme_name: str = None):
        cfg = self.cfg
        description = ""
        colour = cfg.theme.colour

        if theme_name is None:
            description = "You need to provide a theme name!"
            colour = "#ff0000"
        elif not cfg.theme_exists(theme_name):
            description = f"There isn't a theme named {theme_name}!"
            colour = "#ff0000"
        else:
            cfg.delete_theme(theme_name)
            description = f"Theme {theme_name} deleted!"

        await cmdhelper.send_message(ctx, {
            "title": f"🎨 Theme",
            "description": description,
            "colour": colour,
            "footer": cfg.theme.footer,
        })

    @theme.command(name="set", description="Change your theme", usage="[theme]")
    async def change_theme(self, ctx, theme_name: str = None):
        cfg = self.cfg
        description = ""
        colour = cfg.theme.colour
        theme = cfg.get_theme_file(theme_name)

        if theme:
            cfg.set_theme(theme_name)

            colour = cfg.theme.colour
            description = f"Theme set to {theme_name}"
        else:
            colour = "#ff0000"
            description = f"There isn't a theme named {theme_name}"
        
        await cmdhelper.send_message(ctx, {
            "title": f"🎨 Theme",
            "description": description,
            "colour": colour,
            "footer": cfg.theme.footer,
        })
        
        cfg.save()

    async def theme_set(self, ctx, subkey, value):
        cfg = self.cfg
        description = ""

        key = "message_settings" if subkey == "style" else "theme"

        if key == "theme":
            theme = cfg.theme
            theme.__dict__[subkey] = value
            description = f"Theme {subkey} set to {value}"
            cfg.theme.save(notify=False)

        elif key == "message_settings":
            message_settings = cfg.get(key)
            message_settings[subkey] = value
            description = f"Message setting {subkey} set to {value}"

        await cmdhelper.send_message(ctx, {
            "title": f"🎨 Theme",
            "description": description,
            "colour": cfg.theme.colour,
            "footer": cfg.theme.footer,
        })

        cfg.save()

    @theme.command(name="title", description="Set the title of the embed.", usage="[title]")
    async def theme_title(self, ctx, *, title: str):
        await self.theme_set(ctx=ctx, subkey="title", value=title)
        
    @theme.command(name="colour", description="Set the colour of the embed.", usage="[colour]", aliases=["color"])
    async def theme_colour(self, ctx, colour: str):
        await self.theme_set(ctx=ctx, subkey="colour", value=colour)

    @theme.command(name="footer", description="Set the footer of the embed.", usage="[footer]")
    async def theme_footer(self, ctx, *, footer: str):
        await self.theme_set(ctx=ctx, subkey="footer", value=footer)

    @theme.command(name="image", description="Set the image of the embed.", usage="[image]")
    async def theme_image(self, ctx, image: str):
        await self.theme_set(ctx=ctx, subkey="image", value=image)

    @theme.command(name="style", description="Set the style of the embed.", usage="[style]")
    async def theme_style(self, ctx, style: str):
        await self.theme_set(ctx=ctx, subkey="style", value=style)

    @commands.command(name="imagemode", description="Set your theme style to image.", usage="", aliases=["imgmode"])
    async def imagemode(self, ctx):
        await self.theme_set(ctx=ctx, subkey="style", value="image")

    @commands.command(name="textmode", description="Set your theme style to codeblock.", usage="", aliases=["codeblockmode"])
    async def textmode(self, ctx):
        await self.theme_set(ctx=ctx, subkey="style", value="codeblock")

    @commands.command(name="embedmode", description="Set your theme style to embed.", usage="")
    async def embedmode(self, ctx):
        await self.theme_set(ctx=ctx, subkey="style", value="embed")

def setup(bot):
    bot.add_cog(Theming(bot))