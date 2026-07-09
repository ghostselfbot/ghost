import discord
import os
import time
import datetime
import json
import requests
import asyncio
import calendar

from discord.ext import commands
from utils import config
from utils import console
from utils import files
import bot.helpers.cmdhelper as cmdhelper
import bot.helpers.codeblock as codeblock
import bot.helpers.imgembed as imgembed

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = cmdhelper.cog_desc("info", "Info commands")
        self.cfg = config.Config()

    @commands.command(name="info", description="Information commands.", aliases=["information"], usage="")
    async def info(self, ctx, selected_page: int = 1):
        cfg = self.cfg
        pages = cmdhelper.generate_help_pages(self.bot, "Info")

        await cmdhelper.send_message(ctx, {
            "title": f"📋 info commands",
            "description": pages[cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.command(name="iplookup", description="Look up an IP address.", usage="[ip]", aliases=["ipinfo"])
    async def iplookup(self, ctx, ip):
        response = requests.get(f"https://ipapi.co/{ip}/json/").json()

        info = {
            "IP": response["ip"],
            "City": response["city"],
            "Region": response["region"],
            "Country": response["country"],
            "Postal": response["postal"],
            "Latitude": response["latitude"],
            "Longitude": response["longitude"],
            "Timezone": response["timezone"],
            "Org": response["org"]
        }

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "IP Lookup",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()])
        })

    @commands.command(name="userinfo", description="Get information about a user.", aliases=["ui"], usage="[user]")
    async def userinfo(self, ctx, user: discord.User = None):
        if user is None: user = ctx.author

        info = {
            "ID": user.id,
            "Username": user.name,
            "Bot": user.bot,
            "System": user.system,
            "Created at": user.created_at
        }
        
        rich_presences = None

        if ctx.guild is not None:
            user: discord.User = ctx.guild.get_member(user.id)
            if user.nick: info["Nickname"] = user.nick
            info["Joined at"] = user.joined_at
            # info["Desktop status"] = user.desktop_status
            # info["Mobile status"] = user.mobile_status
            # info["Web status"] = user.web_status
            info["Status"] = user.status
            if user.voice: info["In VC"] = user.voice
            # info["Premium"] = user.premium
            if user.activities: rich_presences = [activity.to_dict() for activity in user.activities]
            if user.activity:
                # find the activity that is named custom status in rich_presences and remove it then set info[activities] to the activity
                for activity in rich_presences:
                    if activity["name"].lower() == "custom status":
                        info["Activity"] = activity["state"]
                        rich_presences.remove(activity)
                        break

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "User Info",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()]),
            "thumbnail": user.avatar.url
        })
        
        if rich_presences:
            await ctx.send(
                str(codeblock.Codeblock(
                    title="activities", 
                    extra_title="user", 
                    description=json.dumps(rich_presences, indent=4, sort_keys=True, default=str), 
                    style="json")),
                delete_after=self.cfg.get("message_settings")["auto_delete_delay"]
            )

    @commands.command(name="serverinfo", description="Get information about the server.", aliases=["si"], usage="[id]")
    async def serverinfo(self, ctx, guild_id: int = None):
        if guild_id is None:
            guild = ctx.guild
        else:
            guild = discord.utils.get(self.bot.guilds, id=guild_id)

        if not guild:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You're not part of this guild so I can't provide information.",
                "colour": "#ff0000"
            })
            return

        info = {
            "ID": guild.id,
            "Name": guild.name,
            "Owner": guild.owner,
            # "Region": guild.region,
            "Members": len(guild.members),
            "Roles": len(guild.roles),
            "Channels": len(guild.channels),
            "Created at": guild.created_at
        }

        await cmdhelper.send_message(ctx, {
            "title": "Server Info",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (10 - len(key))} :: {value}" for key, value in info.items()]),
            "thumbnail": guild.icon.url
        })

    @commands.command(name="servericon", description="Get the icon of the server.")
    async def servericon(self, ctx):
        await ctx.send(ctx.guild.icon.url)

    @commands.command(name="webhookinfo", description="Get information about a webhook.", aliases=["wi"], usage="[webhook url]")
    async def webhookinfo(self, ctx, webhook_url):
        try:
            webhook = discord.Webhook.from_url(webhook_url, session=self.bot._connection)
        except:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Invalid webhook URL.",
                "colour": "#ff0000"
            })
            return

        info = {
            "ID": webhook.id,
            "Name": webhook.name,
            "Channel": webhook.source_channel,
            "Guild": webhook.source_guild,
            "Token": "Attached below"
        }

        await cmdhelper.send_message(ctx, {
            "title": "Webhook Info",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "thumbnail": ""
        }, extra_message="```" + webhook.token + "```")

    @commands.command(name="mutualservers", description="Get a list of all members in mutual servers.", usage="[server id]", aliases=["mutualservermembers"])
    async def mutualservers(self, ctx, guild_id: int = None):
        return await ctx.send("> This command may flag your account. For now, it will be disabled until further notice.", delete_after=self.cfg.get("message_settings")["auto_delete_delay"])
        
        # if guild_id is None: guild_id = ctx.guild.id
        # given_guild = self.bot.get_guild(guild_id)
        # if not given_guild:
        #     return await cmdhelper.send_message(ctx, {"title": "Error", "description": "Invalid server ID."})

        # bot_guilds = self.bot.guilds
        # guilds_data = []
        # mutual_server_members = {}
        # formatted_data = {}
        # given_guild_members = {}
        # msg = None
        # read_from_cache = False

        # if not os.path.exists(files.get_application_support() + "/data/cache/guilds.json"):
        #     msg = await cmdhelper.send_message(ctx, {"title": "Mutual Server Members", "description": "This could take a while, watch the console for progress."}, delete_after=False)
        #     console.print_info(f"Fetching members from {len(bot_guilds)} guilds...")

        #     for guild in bot_guilds:
        #         text_channels = [channel for channel in await guild.fetch_channels() if isinstance(channel, discord.TextChannel)]
        #         members = []

        #         try:
        #             discord_members = await guild.fetch_members(channels=text_channels, cache=True, force_scraping=True, delay=0.1)
        #             for member in discord_members:
        #                 if not member.bot: members.append({"id": member.id, "username": member.name})

        #             console.print_success(f"Fetched {len(members)} members from {guild.name}!")
        #         except Exception as e:
        #             console.print_error(f"Failed to fetch members from {guild.name}.")

        #         guilds_data.append({
        #             "id": guild.id,
        #             "name": guild.name,
        #             "members": members
        #         })

        #         await asyncio.sleep(0.3)

        #     with open(files.get_application_support() + "/data/cache/guilds.json", "w") as f:
        #         f.write(json.dumps(guilds_data, indent=4, sort_keys=True, default=str))
        #         console.print_success("Cached guilds data.")
        # else:
        #     console.print_info("Reading guilds from cache...")
        #     console.print_warning("This may be out of date. Clear cache using the 'clearcache' command.")
        #     read_from_cache = True

        #     with open(files.get_application_support() + "/data/cache/guilds.json", "r") as f:
        #         guilds_data = json.load(f)

        # for guild in guilds_data:
        #     if guild["id"] == guild_id:
        #         for member in guild["members"]:
        #             given_guild_members[member["id"]] = member

        # for guild in guilds_data:
        #     for member in guild["members"]:
        #         if member["id"] in given_guild_members and member["id"] != ctx.author.id:
        #             if member["id"] not in mutual_server_members:
        #                 mutual_server_members[member["id"]] = {
        #                     "id": member["id"],
        #                     "username": member["username"],
        #                     "guilds": []
        #                 }
        #             mutual_server_members[member["id"]]["guilds"].append(guild["name"])

        # for member_id, member_data in list(mutual_server_members.items()):
        #     if len(member_data["guilds"]) == 1 and given_guild.name in member_data["guilds"]:
        #         del mutual_server_members[member_id]
        #     else:
        #         formatted_data[member_data["username"]] = member_data["guilds"]

        # description = json.dumps(formatted_data, indent=4, sort_keys=True, default=str)
        # response_codeblock = codeblock.Codeblock(
        #     title="mutual server members",
        #     extra_title=f"guild: {given_guild.name.lower()}",
        #     description=description,
        #     style="json",
        #     footer="this data may be inaccurate" if not read_from_cache else "this is cached data, use the 'clearcache' command and try again"
        # )

        # if len(str(response_codeblock)) > 2000:
        #     console.print_warning("The response is too large, sending as a file instead.")
        #     with open(files.get_application_support() + "/mutual_server_members.json", "w") as f:
        #         f.write(description)

        #     await ctx.send(file=discord.File(files.get_application_support() + "/mutual_server_members.json"), delete_after=self.cfg.get("message_settings")["auto_delete_delay"])
        #     os.remove("mutual_server_members.json")
        #     response_codeblock.description = "The data was too large, so it has been sent as a file instead."

        # console.print_success(f"Completed fetching members from {len(bot_guilds)} guilds!")
        # if msg: await msg.delete()
        # await ctx.send(response_codeblock, delete_after=self.cfg.get("message_settings")["auto_delete_delay"])

    @commands.command(name="avatar", description="Get the avatar of a user.", aliases=["av"], usage="[user]")
    async def avatar(self, ctx, user: discord.User = None):
        cfg = self.cfg

        if user is None:
            user = ctx.author

        if cfg.get("message_settings")["style"] == "codeblock":
            await ctx.send(str(codeblock.Codeblock(title="avatar", extra_title=str(user))) + user.avatar.url, delete_after=cfg.get("message_settings")["auto_delete_delay"])

        else:
            embed = imgembed.Embed(title=f"{user.name}'s avatar", description="The link has been added above for a higher quality image.", colour=cfg.theme.colour)
            embed.set_thumbnail(url=str(user.avatar.url))
            embed.set_footer(text=cfg.theme.footer)
            embed_file = embed.save()

            await ctx.send(content=f"<{user.avatar.url}>", file=discord.File(embed_file, filename="embed.png"), delete_after=cfg.get("message_settings")["auto_delete_delay"])
            os.remove(embed_file)

    @commands.command(name="tickets", description="Get a list of all tickets available in the server.")
    async def tickets(self, ctx):
        tickets = []

        for channel in ctx.guild.channels:
            if str(channel.type) == "text":
                if "ticket" in channel.name.lower():
                    tickets.append(f"#{channel.name}")

        await cmdhelper.send_message(ctx, {
            "title": "Tickets",
            "description": "\n".join(tickets) if tickets else "There were no tickets found."
        })

    @commands.command(name="hiddenchannels", description="List all hidden channels.", aliases=["privchannels", "privatechannels"])
    async def hiddenchannels(self, ctx):
        channels = []

        for channel in ctx.guild.channels:
            if str(channel.type) == "text":
                if channel.overwrites_for(ctx.author.top_role).read_messages == False:
                    channels.append(f"#{channel.name}")

        await cmdhelper.send_message(ctx, {
            "title": "Hidden Channels",
            "description": "\n".join(channels) if channels else "There were no hidden channels found."
        })

    @commands.command(name="crypto", description="Lookup current data on a cryptocurrency.", usage="[cryptocurrency]")
    async def crypto(self, ctx, currency):
        resp = requests.get(f"https://api.coingecko.com/api/v3/coins/{currency}")

        if resp.status_code == 404:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Invalid cryptocurrency."
            })
            return

        data = resp.json()
        info = {
            "Name": currency,
            "Price": f"${data['market_data']['current_price']['usd']}",
            "High 24h": f"${data['market_data']['high_24h']['usd']}",
            "Low 24h": f"${data['market_data']['low_24h']['usd']}",
            "Market Cap": f"${data['market_data']['market_cap']['usd']}",
            "Total Volume": f"${data['market_data']['total_volume']['usd']}",
            "Market Cap Rank": data['market_cap_rank'],
            "All Time High": f"${data['market_data']['ath']['usd']}",
            "All Time Low": f"${data['market_data']['atl']['usd']}",
            "Circulating Supply": f"{data['market_data']['circulating_supply']} {currency}",
            "Total Supply": f"{data['market_data']['total_supply']} {currency}"
        }

        longest_key = max([len(key) for key in info.keys()])

        await cmdhelper.send_message(ctx, {
            "title": "Crypto Info",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()])
        })

    @commands.command(name="bitcoin", description="Get the current data on Bitcoin.", aliases=["btc"])
    async def bitcoin(self, ctx):
        await self.crypto(ctx, "bitcoin")

    @commands.command(name="ethereum", description="Get the current data on Ethereum.", aliases=["eth"])
    async def ethereum(self, ctx):
        await self.crypto(ctx, "ethereum")

    @commands.command(name="tether", description="Get the current data on Tether.", aliases=["usdt"])
    async def tether(self, ctx):
        await self.crypto(ctx, "tether")

    @commands.command(name="dogecoin", description="Get the current data on Dogecoin.", aliases=["doge"])
    async def dogecoin(self, ctx):
        await self.crypto(ctx, "dogecoin")

    @commands.command(name="timestamp", description="Create a relative dynamic timestamp.", usage="[DD MM YYYY HH:MM:SS]")
    async def timestamp(self, ctx, *args):
        try:
            if not args:
                timestamp = int(time.time())
            else:
                date_str = " ".join(args)
                formats = [
                    "%d %m %Y %H:%M:%S",   # 21 03 1800 14:30:00
                    "%d-%m-%Y %H:%M:%S",   # 21-03-1800 14:30:00
                    "%d %B %Y %H:%M:%S",   # 21 March 1800 14:30:00
                    "%d-%m-%Y %H:%M",      # 21-03-1800 14:30
                    "%d %m %Y",            # 21 03 1800
                    "%d-%m-%Y",            # 21-03-1800
                    "%d %B %Y",            # 21 March 1800
                ]
                
                for fmt in formats:
                    try:
                        dt = datetime.datetime.strptime(date_str, fmt)
                        timestamp = calendar.timegm(dt.utctimetuple())
                        break
                    except ValueError:
                        continue
                else:
                    return await cmdhelper.send_message(ctx, {
                        "title": "Error",
                        "description": "Invalid date format! Use `DD MM YYYY HH:MM:SS` or `DD Month YYYY HH:MM:SS`.",
                        "colour": "#ff0000"
                    })

            timestamp_format = f"<t:{timestamp}:R>"

            await ctx.send(f"{timestamp_format}")

        except Exception as e:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"An error occurred: {e}",
                "colour": "#ff0000"
            })

def setup(bot):
    bot.add_cog(Info(bot))
