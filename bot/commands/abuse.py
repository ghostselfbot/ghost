import discord
import requests
import asyncio
import random
import faker
import threading
import subprocess

from discord.ext import commands
from utils import config
from utils import console
import bot.helpers.cmdhelper as cmdhelper

class Abuse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cfg = config.Config()
        self.fake = faker.Faker()
        self.description = cmdhelper.cog_desc("abuse", "Abusive commands")

    @commands.command(name="abuse", description="Abusive commands.", usage="")
    async def abuse(self, ctx, selected_page: int = 1):
        pages = cmdhelper.generate_help_pages(self.bot, "Abuse")

        await cmdhelper.send_message(ctx, {
            "title": f"🎯 abuse commands",
            "description": pages[self.cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[self.cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[self.cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.command(name="spam", description="Spam a channel.", usage="[amount] [message]")
    async def spam(self, ctx, amount: int, *, message: str):
        for _ in range(amount):
            await ctx.send(message)
            await asyncio.sleep(.5)

    @commands.command(name="servernuke", description="Nuke a server.", usage="", aliases=["nukeserver"])
    async def servernuke(self, ctx):
        if ctx.author.guild_permissions.administrator:
            for channel in ctx.guild.channels:
                try:
                    await channel.delete()
                    await asyncio.sleep(.25)
                except:
                    pass

            for role in ctx.guild.roles:
                try:
                    await role.delete()
                    await asyncio.sleep(.25)
                except:
                    pass

            try:
                await ctx.guild.edit(name="Nuked by " + ctx.author.name)
            except:
                pass

            for _ in range(250):
                await ctx.guild.create_text_channel(name="Nuked by " + ctx.author.name)
                await asyncio.sleep(.25)

    @commands.command(name="channelflood", description="Flood guild with a crap ton of channels.", usage="[channel name]")
    async def channelflood(self, ctx, channel_name: str = "random"):
        if ctx.author.guild_permissions.administrator:
            for _ in range(250):
                if channel_name == "random":
                    channel_name = str(random.randint(100000000000000000, 999999999999999999))

                await ctx.guild.create_text_channel(name=channel_name)
                await asyncio.sleep(.25)

    @commands.command(name="channelspam", description="Flood a channel with a message of your choosing.", usage="[msg amount] [message]")
    async def channelspam(self, ctx, msg_amount: int, *, message: str):
        for _ in range(msg_amount):
            await ctx.send(f"> ** **\n> # {message}\n> ** **")
            await asyncio.sleep(.5)

    @commands.command(name="channelping", description="Ping a user in every available channel.", usage="[user] [ping amount]")
    async def channelping(self, ctx, users: str, ping_amount: int = 1, threaded: bool = False):
        headers  = {"Authorization": self.cfg.get("token"), "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
        base_url = "https://discord.com/api"

        async def delete_message(channel_id, message_id):
            try:
                resp = requests.delete(f"{base_url}/channels/{channel_id}/messages/{message_id}", headers=headers)

                while "retry_after" in resp.json() or resp.status_code == 429:
                    await asyncio.sleep(resp.json()["retry_after"])
                    resp = requests.delete(f"{base_url}/channels/{channel_id}/messages/{message_id}", headers=headers)

                return resp
            except Exception as e:
                return e

        async def channelping_thread(channel, user, ping_amount, delay):
            for _ in range(ping_amount):
                resp = requests.post(f"{base_url}/channels/{channel.id}/messages", json={"content": f"{users}"}, headers=headers)

                if "retry_after" in resp.json():
                    console.print_warning(f"Rated limited in #{channel.name}")
                else:
                    console.print_info(f"Sent ping to #{channel.name}!")

                await delete_message(channel.id, resp.json()["id"])
                await asyncio.sleep(1)

                if ping_amount > 1:
                    if delay > 2:
                        console.print_info(f"Waiting {delay} seconds...")
                    await asyncio.sleep(delay)

        def channelping_thread_middleman(channel, user, ping_amount, delay):
            asyncio.run(channelping_thread(channel, user, ping_amount, delay))

        channels         = []
        threads          = []
        default_delay    = 2

        for channel in ctx.guild.channels:
            if str(channel.type) == "text":
                if channel.permissions_for(ctx.guild.me).send_messages:
                    channels.append(channel)

        console.print_info(f"Sending {len(channels) * ping_amount} pings...")

        if threaded:
            for channel in channels:
                _thread = threading.Thread(
                    target=channelping_thread_middleman,
                    args=(
                        channel,
                        users,
                        ping_amount,
                        channel.slowmode_delay if channel.slowmode_delay > default_delay else default_delay,
                        ),
                    daemon=True
                )

                threads.append(_thread)

            for thread in threads:
                thread.start()
                # await asyncio.sleep(2)

            for thread in threads:
                thread.join()
                # await asyncio.sleep(2)
        else:
            for channel in channels:
                await channelping_thread(channel, users, ping_amount, channel.slowmode_delay if channel.slowmode_delay > default_delay else default_delay)

        print()
        console.print_info("All pings done! Clearing console in 15 seconds...")
        await asyncio.sleep(15)
        subprocess.run("clear", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print()
        console.print_banner()

    @commands.command(name="massping", description="Ping every user in a server.", aliases=["hahafunny"], usage="[msg amount] [guild id]")
    async def massping(self, ctx, message_amount=5, guild_id=None):
        guild = ctx.guild
        if guild_id:
            guild = await self.bot.fetch_guild(guild_id)

        text_channels = [channel for channel in await guild.fetch_channels() if isinstance(channel, discord.TextChannel)]
        members = [f"<@{member.id}>" for member in await guild.fetch_members(channels=text_channels, cache=True, force_scraping=True, delay=0.1) if not member.bot]
        message = ""
        messages = []

        for member in members:
            if len(message) < 1950:
                message += member
            else:
                messages.append(message)
                message = ""

        messages.append(message)

        for _ in range(message_amount):
            for message in messages:
                try:
                    await ctx.send(message, delete_after=0)
                except Exception as e:
                    return console.print_error("Failed to send mentions. Most likely due to mention limit set.")
                await asyncio.sleep(0.75)

    @commands.command(name="pollspam", description="Flood a channel with polls.")
    async def pollspam(self, ctx):
        # if not ctx.guild.me.guild_permissions.create_expressions:
        #     console.print_error("Bot does not have the necessary permissions to manage messages.")
        #     return

        for i in range(25):
            try:
                resp = requests.post(f"https://discord.com/api/channels/{ctx.channel.id}/messages", headers={
                    "Authorization": f"{self.cfg.get('token')}",
                    "Content-Type": "application/json"
                }, json={
                    "content": "",
                    "poll": {
                        "question": {
                            "text": "".join(["﷽" for i in range(300)])
                        },
                        "answers": [
                            {
                                "poll_media": {
                                    "text": "".join(["﷽" for i in range(55)])
                                }
                            } for i in range(10)
                        ],
                        "allow_multiselect": False,
                        "duration": 24,
                        "layout_type": 1
                    }
                })

                if resp.status_code != 200:
                    if "missing permissions" in resp.content.lower():
                        console.print_error("Bot does not have the necessary permissions to manage messages.")
                        return resp.json()

                    console.print_error(f"Failed to create poll: {resp.json()}")

                console.print_success(f"Poll created.")
                await asyncio.sleep(.53)

            except Exception as e:
                console.print_error(f"Failed to create poll: {e}")
                return e

        console.print_info("Poll spam complete.")

def setup(bot):
    bot.add_cog(Abuse(bot))
