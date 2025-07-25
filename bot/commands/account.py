import requests
import discord
import os
import sys
import json
import asyncio
import time

from discord.ext import commands
from utils import config
from utils import console
from utils import files
import bot.helpers.cmdhelper as cmdhelper
from bot.helpers import parse_external_asset

class Account(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = cmdhelper.cog_desc("account", "Account commands")
        self.cfg = config.Config()
        self.headers = {
            "Authorization": f"{self.cfg.get('token')}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    @commands.command(name="account", description="Account commands.", aliases=["acc"], usage="")
    async def account(self, ctx, selected_page: int = 1):
        cfg = self.cfg
        pages = cmdhelper.generate_help_pages(self.bot, "Account")

        await cmdhelper.send_message(ctx, {
            "title": f"📥 account commands",
            "description": pages[cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.command(name="backups", description="List your backups.", usage="")
    async def backups(self, ctx):
        if not os.path.exists(files.get_application_support() + "/backups/"):
            os.mkdir(files.get_application_support() + "/backups/")

        backups = os.listdir(files.get_application_support() + "/backups/")

        if len(backups) == 0:
            await cmdhelper.send_message(ctx, {"title": "Backups", "description": "No backups found.", "colour": "#ff0000"})
            return
        
        description = ""
        for backup in backups:
            if backup.endswith(".json"):
                description += f"{backup[:len(backup)-5]}\n"

        await cmdhelper.send_message(ctx, {"title": "Backups", "description": description})
            
    @commands.group(name="backup", description="Backup commands.", usage="")
    async def backup(self, ctx):
        cfg = self.cfg

        if ctx.invoked_subcommand is None:
            description = ""
            for sub_command in self.backup.commands:
                if cfg.get("message_settings")["style"] == "codeblock":
                    description += f"backup {sub_command.name} :: {sub_command.description}\n"
                else:
                    description += f"**{self.bot.command_prefix}backup {sub_command.name}** {sub_command.description}\n"
            
            await cmdhelper.send_message(ctx, {"title": "Backup Commands", "description": description})

    @backup.command(name="view", description="View a backup.", usage="[backup]")
    async def backup_view(self, ctx, backup: str):
        HEADLESS = "DISPLAY" not in os.environ and sys.platform == "linux"
        
        if not os.path.exists(files.get_application_support() + "/backups/"):
            os.mkdir(files.get_application_support() + "/backups/")
        backup_path = files.get_application_support() + f"/backups/{backup}.json"

        if not os.path.exists(backup_path):
            await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Backup {backup} doesn't exist.", "colour": "ff0000"})
            return
        
        if HEADLESS:
            with open(backup_path, "r") as f:
                backup_desc = json.loads(f.read())
            console.print_info(f"Backup {backup}:\n{json.dumps(backup_desc, indent=4)}")
            await cmdhelper.send_message(ctx, {"title": "Backup", "description": f"See console for backup {backup}."})
        else:
            files.open_file_in_editor(backup_path)
            await cmdhelper.send_message(ctx, {"title": "Backup", "description": f"Opened backup {backup} in explorer."})

    @backup.command(name="account", description="Backup your account information.", usage="")
    async def backup_account(self, ctx):
        backup = {
            "created_at": time.time(),
            "type": "account",
            "info": {
                "id": self.bot.user.id,
                "name": self.bot.user.name,
                "display_name": self.bot.user.display_name,
                "accent_colour": self.bot.user.accent_colour,
                "avatar": self.bot.user.avatar.url,
                "banner": self.bot.user.banner.url,
                "bio": self.bot.user.bio
            }
        }

        if not os.path.exists(files.get_application_support() + "/backups/"):
            os.mkdir(files.get_application_support() + "/backups/")

        with open(files.get_application_support() + "/backups/account.json", "w") as f:
            f.write(json.dumps(backup))

        await cmdhelper.send_message(ctx, {"title": "Account Backup", "description": f"Saved some information about your account in account.json"})

    @backup.command(name="friends", description="Backup your friends.", usage="")
    async def backup_friends(self, ctx):
        backup = {
            "created_at": time.time(),
            "type": "friends",
            "list": []
        }

        for friend in self.bot.friends:
            if friend.type == discord.RelationshipType.friend:
                backup["list"].append({
                    "username": friend.user.name,
                    "id": friend.user.id
                })

        if not os.path.exists(files.get_application_support() + "/backups/"):
            os.mkdir(files.get_application_support() + "/backups/")

        with open(files.get_application_support() + "/backups/friends.json", "w") as f:
            f.write(json.dumps(backup))
        
        console.success(f"Created a backup of your friends.")
        console.info(f"Backup created at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(backup['created_at']))}")
        console.info(f"Backup saved to {files.get_application_support()}/backups/friends.json")
        await cmdhelper.send_message(ctx, {"title": "Friends Backup", "description": f"Saved {len(self.bot.friends)} friends to friends.json. See console for more information."})

    @backup.command(name="guilds", description="Backup your guilds.", usage="", aliases=["servers"])
    async def backup_guilds(self, ctx):
        backup = {
            "created_at": time.time(),
            "type": "guilds",
            "list": []
        }

        for guild in self.bot.guilds:
            invite = guild.vanity_url if guild.vanity_url else None

            if not invite:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel) and channel.permissions_for(guild.me).create_instant_invite:
                        try:
                            invite = await channel.create_invite(max_age=0, max_uses=1, unique=True)
                        except Exception as e:
                            break
                        if invite: break
            
            if invite:
                console.print_success(f"Got invite for {guild.name}.")
            else:
                console.print_warning(f"Failed to get invite for {guild.name}.")
                invite = "None"
            
            backup["list"].append({
                "name": guild.name,
                "id": guild.id,
                "invite": str(invite)
            })
            
            await asyncio.sleep(0.75)

        if not os.path.exists(files.get_application_support() + "/backups/"):
            os.mkdir(files.get_application_support() + "/backups/")

        with open(files.get_application_support() + "/backups/guilds.json", "w") as f:
            f.write(json.dumps(backup))

        console.success(f"Created a backup of your guilds.")
        console.info(f"Backup created at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(backup['created_at']))}")
        console.info(f"Backup saved to {files.get_application_support()}/backups/guilds.json")

        await cmdhelper.send_message(ctx, {"title": "Guilds Backup", "description": f"Saved {len(self.bot.guilds)} guilds to guilds.json"})

    @backup.command(name="restore", description="Restore a backup.", usage="[backup]")
    async def backup_restore(self, ctx, backup: str):
        if not os.path.exists(files.get_application_support() + "/backups/"):
            os.mkdir(files.get_application_support() + "/backups/")
        backup_path = files.get_application_support() + f"/backups/{backup}.json"
        cfg = self.cfg
        headers = {
                    "Authorization": f"{cfg.get('token')}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }

        if not os.path.exists(backup_path):
            await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Backup {backup} doesn't exist.", "colour": "ff0000"})
            return
            
        # if not backup.endswith(".json"):
        #     await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Backup {backup} is not a JSON file.", "colour": "ff00000"})
        #     return
        
        await cmdhelper.send_message(ctx, {"title": "WARNING", "description": f"Restore backup is currenting a WIP feature. This could also result in your account getting banned! Please use with caution. Look at the console for backup progress.", "colour": "ebde34"})
        
        with open(backup_path, "r") as f:
            backup = json.loads(f.read())

        if backup["type"] == "friends":
            for friend in backup["list"]:
                user_resp = requests.get(f"https://discord.com/api/v9/users/{friend['id']}", headers=headers)
                if user_resp.status_code != 200:
                    console.print_error(f"Failed to get {friend['username']}.")
                    return

                user = discord.User(state=self.bot._connection, data=user_resp.json())
                
                try:
                    user.send_friend_request()
                except Exception as e:
                    console.print_error(f"Failed to add {friend['username']}.")
                    console.print_error(e)
                    return
                
                console.print_success(f"Added {friend['username']}!")
                await asyncio.sleep(1)

            await cmdhelper.send_message(ctx, {"title": "Restore Backup", "description": f"Restored {len(backup['list'])} friends. They have been sent a friend request."})

        elif backup["type"] == "guilds":
            invites = [guild["invite"] for guild in backup["list"]]
            invites = [invite for invite in invites if invite != "None"]
            await cmdhelper.send_message(ctx, {"title": "Restore Backup", "description": f"I'm unable to automatically join guilds. Please manually join the following guilds. This will delete in {cfg.get('message_settings')['auto_delete_delay']} seconds."})
            await ctx.send("\n".join(invites), delete_after=cfg.get("message_settings")["auto_delete_delay"])

        else:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Unknown backup type {backup['type']}. Ghost backup restore only supports backups made using Ghost.", "colour": "ff0000"})

    @commands.command(name="hypesquad", description="Change your hypesquad.", usage="[hypesquad]", aliases=["changehypesquad"])
    async def hypesquad(self, ctx, house: str = ""):
        houses = {
            "bravery": "1",
            "brilliance": "2",
            "balance": "3"
        }
        house = house.lower()

        if house not in houses or house == "" or house == None:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Invalid house. Please choose from Bravery, Brilliance and Balance.", "colour": "ff0000"})
            return
        
        resp = requests.post("https://discord.com/api/v9/hypesquad/online", headers=self.headers, json={"house_id": houses[house]})

        if resp.status_code != 204:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Failed to change hypesquad. {resp.status_code} {resp.text}", "colour": "ff0000"})
            return
        
        await cmdhelper.send_message(ctx, {"title": "Hypesquad", "description": f"Changed hypesquad to {house}."})

    @commands.command(name="status", description="Change your status.", usage="[status]", aliases=["changestatus"])
    async def status(self, ctx, status: str):
        statuses = {
            "online": "online",
            "idle": "idle",
            "dnd": "dnd",
            "invisible": "invisible"
        }
        status = status.lower()

        if status not in statuses:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Invalid status. Please choose from Online, Idle, DND and Invisible.", "colour": "ff0000"})
            return
        
        await self.bot.change_presence(status=discord.Status.try_value(status))
        await cmdhelper.send_message(ctx, {"title": "Status", "description": f"Changed status to {status}."})

    @commands.command(name="customstatus", description="Change your custom status.", usage="[status]", aliases=["changecustomstatus"])
    async def customstatus(self, ctx, *, status: str):
        await self.bot.change_presence(activity=discord.CustomActivity(name=status))
        await cmdhelper.send_message(ctx, {"title": "Custom Status", "description": f"Changed custom status to {status}."})

    @commands.command(name="clearstatus", description="Clear your custom status.", usage="")
    async def clearstatus(self, ctx):
        await self.bot.change_presence(activity=None)
        await cmdhelper.send_message(ctx, {"title": "Clear Status", "description": "Cleared custom status."})

    @commands.command(name="playing", description="Change your playing status.", usage="[status]", aliases=["changeplaying"])
    async def playing(self, ctx, *, status: str):
        game = discord.Game(status)
        await self.bot.change_presence(activity=game, edit_settings=False)
        await cmdhelper.send_message(ctx, {"title": "Playing Status", "description": f"Changed playing status to {status}."})

    @commands.command(name="streaming", description="Change your streaming status.", usage="[status]", aliases=["changestreaming"])
    async def streaming(self, ctx, *, status: str):
        stream = discord.Streaming(name=status, url="https://twitch.tv/ghost")
        await self.bot.change_presence(activity=stream, edit_settings=False)
        await cmdhelper.send_message(ctx, {"title": "Streaming Status", "description": f"Changed streaming status to {status}."})

    @commands.command(name="nickname", description="Change your nickname.", usage="[nickname]", aliases=["changenickname", "nick"])
    async def nickname(self, ctx, *, nickname: str):
        if ctx.guild is None:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": "You can only change your nickname in a server.", "colour": "ff0000"})
            return
        
        if not ctx.guild.me.guild_permissions.change_nickname:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": "I don't have permission to change nicknames.", "colour": "ff0000"})
            return
        
        await ctx.guild.me.edit(nick=nickname)
        await cmdhelper.send_message(ctx, {"title": "Nickname", "description": f"Changed nickname to {nickname}."})

    @commands.command(name="clearnickname", description="Clear your nickname.", usage="", aliases=["resetnickname", "clearnick", "resetnick"])
    async def clearnickname(self, ctx):
        if ctx.guild is None:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": "You can only change your nickname in a server.", "colour": "ff0000"})
            return
        
        if not ctx.guild.me.guild_permissions.change_nickname:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": "I don't have permission to change nicknames.", "colour": "ff0000"})
            return
        
        await ctx.guild.me.edit(nick=None)
        await cmdhelper.send_message(ctx, {"title": "Nickname", "description": "Cleared nickname."})

    @commands.command(name="discordtheme", description="Change your discord theme.", usage="[theme]", aliases=["changetheme"])
    async def discordtheme(self, ctx, theme: str):
        themes = ["dark", "light"]
        theme = theme.lower()

        if theme not in themes:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Invalid theme. Please choose from Dark and Light.", "colour": "ff0000"})
            return
        
        resp = requests.patch("https://discord.com/api/v9/users/@me/settings", headers=self.headers, json={"theme": theme})

        if resp.status_code != 200:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Failed to change theme. {resp.status_code} {resp.text}", "colour": "ff0000"})
            return
        
        await cmdhelper.send_message(ctx, {"title": "Theme", "description": f"Changed theme to {theme}."})

    @commands.command(name="yoinkrpc", description="Yoink someone's RPC.", usage="[user]", aliases=["rpcyoink", "stealrpc", "stealrichpresence", "yoinkrichpresence", "clonerpc", "clonerichpresence"])
    async def yoinkrpc(self, ctx, user, guild_id: int = None):
        cfg = self.cfg
        guild = None
        
        if not user:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": "You need to provide a user to yoink RPC from.", "colour": "ff0000"})
            return
        
        if isinstance(user, str):
            if user.startswith("<@") and user.endswith(">"):
                user = int(user[2:-1])
            else:
                user = int(user)
        
        if user == self.bot.user.id:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": "You can't yoink your own rich presence..", "colour": "ff0000"})
            return
        
        if guild_id is None:
            guild = ctx.guild
        else:
            guild = self.bot.get_guild(guild_id)
        
        # member = discord.utils.get(guild.members, id=user)
        member = await guild.fetch_member(user) if guild else None
        
        if not member:
            console.print_warning("Couldn't find member. Scraping members in attempt to find member...")
            try:
                text_channels = [channel for channel in await guild.fetch_channels() if isinstance(channel, discord.TextChannel)]
                members = await guild.fetch_members(channels=text_channels, cache=True, force_scraping=True, delay=0.2)
                
                for member in members:
                    if member.id == user:
                        break
            except Exception as e:
                console.print_error("Failed to scrape members.")
                await cmdhelper.send_message(ctx, {"title": "Error", "description": f"Failed to scrape members. Try using `yoinkmemberrpc <@{user}>` in a server this member is in.", "colour": "ff0000"})
                return
        
        activities = member.activities
        rpc = None
        
        if len(activities) == 0:
            await cmdhelper.send_message(ctx, {"title": "Error", "description": "User has no RPC.", "colour": "ff0000"})
            return
        
        with open(files.get_application_support() + "/rpc.json", "w") as f:
            json.dump([activity.to_dict() for activity in activities], f)
        
        if len(activities) > 1:
            for activity in activities:
                if isinstance(activity, discord.Activity):
                    if activity.application_id:
                        rpc = activity
                        break
                
        else:
            rpc = activities[0]
            return await cmdhelper.send_message(ctx, {"title": "Error", "description": "User has no yoinkable RPC.", "colour": "ff0000"})
        
        asset_data_resp = requests.get(f"https://discord.com/api/v9/oauth2/applications/{rpc.application_id}/assets")
        
        if asset_data_resp.status_code == 200:
            assets = asset_data_resp.json()
            print(assets)
        
        assets = {
            "large_image": parse_external_asset(rpc.assets.get("large_image", "")),
            "large_text": rpc.assets.get("large_text", ""),
            "small_image": parse_external_asset(rpc.assets.get("small_image", "")),
            "small_text": rpc.assets.get("small_text", ""),
        }
        
        current_rpc = cfg.get_rich_presence()
        
        current_rpc.enabled = True
        current_rpc.client_id = rpc.application_id
        current_rpc.state = rpc.state
        current_rpc.details = rpc.details
        current_rpc.name = rpc.name
        current_rpc.large_image = assets["large_image"]
        current_rpc.large_text = assets["large_text"]
        current_rpc.small_image = assets["small_image"]
        current_rpc.small_text = assets["small_text"]

        current_rpc.save()
        
        await cmdhelper.send_message(ctx, {
            "title": "Yoink RPC",
            "description": f"Yoinked RPC from {member.name}. Restarting to apply changes...",
            "colour": "ebde34"
        })
        
        cfg.save()
        
        await ctx.invoke(self.bot.get_command("restart"))
        
    @commands.command(name="yoinkmemberrpc", description="yoinkrpc for member pings only!", usage="[member]")
    async def yoinkmemberrpc(self, ctx, member: discord.Member):
        await ctx.invoke(self.yoinkrpc, member)

def setup(bot):
    bot.add_cog(Account(bot))