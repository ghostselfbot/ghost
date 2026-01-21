import requests
import discord
import os
import random
import mimetypes
import shutil

from discord.ext import commands
from utils import config, files
import bot.helpers.cmdhelper as cmdhelper

class Img(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = cmdhelper.cog_desc("img", "Image commands")
        self.cfg = config.Config()

    @commands.command(name="img", description="Image commands.", aliases=["image"], usage="")
    async def img(self, ctx, selected_page: int = 1):
        cfg = self.cfg
        pages = cmdhelper.generate_help_pages(self.bot, "Img")

        await cmdhelper.send_message(ctx, {
            "title": f"🖼️ image commands",
            "description": pages[cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.command(name="gato", description="Get a random cat picture.", aliases=["cat", "catpic"], usage="")
    async def gato(self, ctx):
        cfg = self.cfg
        resp = requests.get("https://api.alexflipnote.dev/cats")
        image = resp.json()["file"]

        await ctx.send(image)

    @commands.command(name="doggo", description="Get a random dog picture.", aliases=["dog", "dogpic"], usage="")
    async def doggo(self, ctx):
        cfg = self.cfg
        resp = requests.get("https://api.alexflipnote.dev/dogs")
        image = resp.json()["file"]

        await ctx.send(image)

    @commands.command(name="bird", description="Get a random bird picture.", aliases=["birb", "birdpic"], usage="")
    async def birb(self, ctx):
        cfg = self.cfg
        resp = requests.get("https://api.alexflipnote.dev/birb")
        image = resp.json()["file"]

        await ctx.send(image)

    @commands.command(name="fox", description="Get a random fox picture.", aliases=["foxpic"], usage="")
    async def fox(self, ctx):
        cfg = self.cfg
        resp = requests.get("https://randomfox.ca/floof/")
        image = resp.json()["image"]

        await ctx.send(image)

    @commands.command(name="minion", description="Get a random minion meme.", aliases=["minionmeme"], usage="")
    async def minion(self, ctx):
        cfg = self.cfg
        resp = requests.get("https://benny.fun/api/minion?json=true")
        image = resp.json()["url"]

        await ctx.send(image, delete_after=cfg.get("message_settings")["auto_delete_delay"])

    @commands.command(name="achievement", description="Make a custom Minecraft achievement.", aliases=["mcachievement"], usage="[icon] [text]")
    async def achievement(self, ctx, given_icon: str = None, *, text: str = None):
        base_url = "https://api.alexflipnote.dev/achievement"
        session = requests.session()
        icons = None
        icons_resp = session.get(f"{base_url}?icon=0")
        if icons_resp.status_code == 200:
            icons = icons_resp.json()

        icons_text = ""
        for icon in icons:
            icons_text += f"{icon} :: {icons[icon]}\n> "

        if given_icon and not given_icon.isdigit():
            for icon in icons:
                if icons[icon].lower() == given_icon.lower():
                    given_icon = icon

        if not given_icon or not given_icon.isdigit() and given_icon.lower() not in [icons[i] for i in icons]:
            return await cmdhelper.send_message(ctx, {
                    "title": "Error",
                    "description": f"Please chose an icon from the list below.",
                    "colour": "ff0000"
            }, extra_message=f"> ```asciidoc\n> {icons_text}```")

        if not text:
            return await cmdhelper.send_message(ctx, {
                    "title": "Error",
                    "description": "Please specify what text you want in the achievement",
                    "colour": "ff0000"
            })

        achievement_resp = session.get(f"{base_url}?text={text.replace(' ', '+')}&icon={given_icon}", stream=True)
        if achievement_resp.status_code == 200:
            with open(files.get_application_support() + "/data/cache/achievement.png", "wb") as photo_file:
                shutil.copyfileobj(achievement_resp.raw, photo_file)

            await ctx.send(file=discord.File(r"data/cache/achievement.png"))
            os.remove("data/cache/achievement.png")
        else:
            return await cmdhelper.send_message(ctx, {
                    "title": "Error",
                    "description": "Failed to generate achievement. API must be down...",
                    "colour": "ff0000"
            })

    @commands.command(name="challenge", description="Make a custom Minecraft challenge.", aliases=["mcchallenge"], usage="[icon] [text]")
    async def challenge(self, ctx, given_icon: str = None, *, text: str = None):
        base_url = "https://api.alexflipnote.dev/challenge"
        session = requests.session()
        icons = None
        icons_resp = session.get(f"{base_url}?icon=0")
        if icons_resp.status_code == 200:
            icons = icons_resp.json()

        icons_text = ""
        for icon in icons:
            icons_text += f"{icon} :: {icons[icon]}\n> "

        if given_icon and not given_icon.isdigit():
            for icon in icons:
                if icons[icon].lower() == given_icon.lower():
                    given_icon = icon

        if not given_icon or not given_icon.isdigit() and given_icon.lower() not in [icons[i] for i in icons]:
            return await cmdhelper.send_message(ctx, {
                    "title": "Error",
                    "description": f"Please chose an icon from the list below.",
                    "colour": "ff0000"
            }, extra_message=f"> ```asciidoc\n> {icons_text}```")

        if not text:
            return await cmdhelper.send_message(ctx, {
                    "title": "Error",
                    "description": "Please specify what text you want in the achievement",
                    "colour": "ff0000"
            })

        achievement_resp = session.get(f"{base_url}?text={text.replace(' ', '+')}&icon={given_icon}", stream=True)
        if achievement_resp.status_code == 200:
            with open(files.get_application_support() + "/data/cache/challenge.png", "wb") as photo_file:
                shutil.copyfileobj(achievement_resp.raw, photo_file)

            await ctx.send(file=discord.File(r"data/cache/challenge.png"))
            os.remove("data/cache/challenge.png")
        else:
            return await cmdhelper.send_message(ctx, {
                    "title": "Error",
                    "description": "Failed to generate challenge. API must be down...",
                    "colour": "ff0000"
            })
        
    @commands.command(name="discordmessage", description="Create a fake Discord message.", aliases=["fakediscordmessage", "fakediscordmsg", "fakediscord"], usage="[user] [message]")
    async def discordmessage(self, ctx, user: discord.User = None, *, message: str = None):
        if not user:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Please specify a user to make the message from.",
                "colour": "#ff0000"
            })

        if not message:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Please specify a message to send.",
                "colour": "#ff0000"
            })

        response = requests.get(f"https://benny.fun/api/discordmessage?avatar_url={user.avatar.url}&username={user.name}&text={message}")

        if response.status_code == 200:
            with open(files.get_application_support() + "/data/cache/discordmessage.png", "wb") as file:
                file.write(response.content)

            await ctx.send(file=discord.File(files.get_application_support() + "/data/cache/discordmessage.png"))
            os.remove(files.get_application_support() + "/data/cache/discordmessage.png")
        else:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Failed to generate discord message.",
                "colour": "#ff0000"
            })

    @commands.command(name="searchimage", description="Search for an image on google", usage="[query]", aliases=["searchimg", "imgsearch", "imagesearch"])
    async def searchimage(self, ctx, *, query):
        cfg = self.cfg
        api_key = cfg.get("apis")["serpapi"]
        
        if api_key == "":
            return await cmdhelper.send_message(ctx, {
                "title": "Image Search",
                "description": "Please provide a SerpAPI key in settings > apis to use this command.",
                "colour": "#ff0000",
                "footer": cfg.theme.footer,
            })
        
        base_url = "https://serpapi.com/search.json?"

        params = {
            "q": query.replace(" ", "+"),
            "engine": "google_images",
            "ijn": 0,
            "api_key": api_key
        }

        attempting_msg = await ctx.send(f"> Starting search for `{query}`.")

        url = base_url + "&".join(f"{param}={params[param]}" for param in params)
        data = requests.get(url)

        if data.status_code == 200:
            await attempting_msg.delete()

            body = data.json()

            if body["search_metadata"]["status"] != "Success":
                await cmdhelper.send_message(ctx, {
                    "title": "Image Search",
                    "description": "The search failed, try another query.",
                    "colour": "#ff0000",
                    "footer": cfg.theme.footer,
                })
            else:
                if "suggested_searches" not in body:
                    await cmdhelper.send_message(ctx, {
                        "title": "Image Search",
                        "description": "The search failed, try another query.",
                        "colour": "#ff0000",
                        "footer": cfg.theme.footer,
                    })

                else:
                    images_results = body["images_results"]
                    amount_to_send = len(images_results)
                    images = []

                    if len(images_results) > 4:
                        await cmdhelper.send_message(ctx, {
                            "title": "Image Search",
                            "description": f"We found {len(images_results)} results for {query}. A random result will be sent.",
                            "colour": cfg.theme.colour,
                            "footer": cfg.theme.footer
                        })


                    image_to_send = random.randint(0, amount_to_send - 1)

                    image = images_results[image_to_send]["original"]
                    res = requests.get(image)
                    if "content-type" in res.headers:
                        extension = str(mimetypes.guess_extension(res.headers["content-type"])).replace(".", "")

                        if extension in ["jpeg", "png", "jpg"]:
                            new_name = str(random.randint(1000,9999)) + f".{extension}"

                            with open(files.get_application_support() + f"/data/cache/{new_name}", "wb") as file:
                                file.write(res.content)

                                images.append(new_name)

                    await ctx.send(files=[discord.File(f"data/cache/{image}") for image in images])

                    for image in images:
                        os.remove(f"data/cache/{image}")
        else:
            await attempting_msg.delete()
            await cmdhelper.send_message(ctx, {
                "title": "Image Search",
                "description": "The search failed, try another query.",
                "colour": "#ff0000",
                "footer": cfg.theme.footer,
            })

def setup(bot):
    bot.add_cog(Img(bot))
