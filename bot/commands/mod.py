import discord
import asyncio
import datetime
import requests

from discord.ext import commands
from utils import config
from utils import console
from utils import files
import bot.helpers.cmdhelper as cmdhelper

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = cmdhelper.cog_desc("mod", "Moderation commands")
        self.cfg = config.Config()

    @commands.command(name="mod", description="Moderation commands.", aliases=["moderation"], usage="")
    async def mod(self, ctx, selected_page: int = 1):
        cfg = self.cfg
        pages = cmdhelper.generate_help_pages(self.bot, "Mod")

        await cmdhelper.send_message(ctx, {
            "title": f"👮 mod commands",
            "description": pages[cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.command(name="clear", description="Clear a number of messages.", aliases=["purge"], usage="[number]")
    async def clear(self, ctx, number: int):
        def is_me(m):
            if ctx.channel.permissions_for(m.author).manage_messages:
                return True
            else:
                return m.author == self.bot.user

        deleted = []

        if isinstance(ctx.channel, discord.DMChannel):
            async for msg in ctx.channel.history(limit=number):
                if msg.author == self.bot.user:
                    deleted.append(msg)
                    await msg.delete()
                    await asyncio.sleep(0.75)

        else:
            deleted = await ctx.channel.purge(limit=number + 1, check=is_me)

        await cmdhelper.send_message(ctx, {
            "title": "Clear",
            "description": f"Cleared {len(deleted) - 1} messages."
        })
        
    @commands.command(name="dmpurge", description="Purge a number of messages in a DM.", usage="[number] [user id]")
    async def dmpurge(self, ctx, number: int, user_id: int):
        user = self.bot.get_user(user_id)
        
        if isinstance(user, discord.User):
            latest_msg = [msg async for msg in user.dm_channel.history(limit=1)][0]
            context = await self.bot.get_context(latest_msg)
            channel = context.channel
            messages = [msg async for msg in channel.history(limit=number) if msg.author.id == self.bot.user.id]
            
            for i, msg in enumerate(messages):
                if i % 5 == 0:
                    await asyncio.sleep(1)
                
                await msg.delete()
                await asyncio.sleep(0.75)
                
            await cmdhelper.send_message(ctx, {
                "title": "DM Purge",
                "description": f"Purged {len(messages)} messages."
            })
            
        else:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "User not found.",
                "colour": "ff0000"
            })

    @commands.command(name="purgechat", description="Purge the entire chat.", usage="")
    async def purgechat(self, ctx):
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })

        delete = await ctx.channel.purge()
        await cmdhelper.send_message(ctx, {
            "title": "Chat Purge",
            "description": f"Purged {len(delete)} messages."
        })

    @commands.command(name="dumpchat", description="Get the chats history.", usage="[message count] [channel id]")
    async def dumpchat(self, ctx, count: int, channel_id: int = None):
        channel = ctx.channel if channel_id is None else self.bot.get_channel(channel_id)
        messages = [message async for message in channel.history(limit=count)]
        # dump = "\n".join([f"{str(message.created_at).split('.')[0]}|{message.author.id}|{message.author.name} : {message.content}" for message in messages])
        
        dump = ""
        for message in messages:
            attachments = [f"[{attachment.filename}]({attachment.url})" for attachment in message.attachments]
            attachments = "\n".join(attachments)
            
            if attachments:
                dump += f"{str(message.created_at).split('.')[0]}|{message.author.id}|{message.author.name} : {message.content}\n{attachments}\n"
            else:
                dump += f"{str(message.created_at).split('.')[0]}|{message.author.id}|{message.author.name} : {message.content}\n"

        with open(files.get_application_support() + f"/data/{channel.id}-dump.txt", "w") as f:
            f.write(dump)

        await ctx.send(file=discord.File(f"data/{channel.id}-dump.txt"))

    @commands.command(name="firstmessage", description="Get the first message in the chat.", usage="")
    async def firstmessage(self, ctx):
        waiting = await ctx.send("> Fetching first message...")

        messages = [message async for message in ctx.channel.history(limit=1, oldest_first=True)]
        message = messages[0]
    
        attachments = [f"[{attachment.filename}]({attachment.url})" for attachment in message.attachments]
        attachments = "\n".join(attachments)

        await waiting.delete()
        await cmdhelper.send_message(ctx, {
            "title": "First Message",
            "description": f"{message.author.name}: {message.content}" if not attachments else + "\n".join(attachments)
        }, extra_message=message.jump_url)

    @commands.command(name="lock", description="Lock the channel.", usage="")
    async def lock(self, ctx):
        if not ctx.message.author.guild_permissions.manage_channels:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })
            return

        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await cmdhelper.send_message(ctx, {
            "title": "Lock",
            "description": "Channel locked."
        })

    @commands.command(name="unlock", description="Unlock the channel.", usage="")
    async def unlock(self, ctx):
        if not ctx.message.author.guild_permissions.manage_channels:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })
            return

        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await cmdhelper.send_message(ctx, {
            "title": "Unlock",
            "description": "Channel unlocked."
        })

    @commands.command(name="banlist", description="List all banned members.", usage="")
    async def banlist(self, ctx):
        if not ctx.message.author.guild_permissions.ban_members:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })
            return

        bans = [entry async for entry in ctx.guild.bans(limit=2000)]

        if len(bans) == 0:
            await cmdhelper.send_message(ctx, {
                "title": "Banlist",
                "description": "No members are banned."
            })

        else:
            description = ""

            for ban in bans:
                description += f"{ban.user.name}:{ban.user.id}\n"

            await cmdhelper.send_message(ctx, {
                "title": "Banlist",
                "description": description
            })

    async def ban_helper(self, ctx, member, action="ban"):
        user = None
        
        try:
            if "<@" in member:
                _id = int(member[2:-1])
            else:
                _id = int(member)
                
            user = discord.utils.get(self.bot.users, id=_id)
                
        except Exception as e:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"Failed to find user: {e}",
                "colour": "ff0000"
            })
            
        if user is None:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Failed to find user.",
                "colour": "ff0000"
            })
            
        bans = [user async for user in ctx.guild.bans(limit=2000)]
        
        if action == "ban" and any(ban.user.id == user.id for ban in bans):
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"User {user.name} is already banned.",
                "colour": "ff0000"
            })
        elif action == "unban" and not any(ban.user.id == user.id for ban in bans):
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"User {user.name} is not banned.",
                "colour": "ff0000"
            })
            
        return user

    @commands.command(name="ban", description="Ban a member from the command server.", usage="[member] [reason]")
    async def ban(self, ctx, member, *, reason=None):
        if not ctx.message.author.guild_permissions.ban_members:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })
            return
        
        user = await self.ban_helper(ctx, member, action="ban")
        if user is None:
            return

        try:
            await ctx.guild.ban(user, reason=reason)
            await cmdhelper.send_message(ctx, {
                "title": "Ban",
                "description": f"Banned {user.name}" + (f" for reason: {reason}" if reason else "")
            })

        except Exception as e:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"{e}",
                "colour": "ff0000"
            })

    @commands.command(name="unban", description="Unban a member from the command server.", usage="[user] [reason]")
    async def unban(self, ctx, member, *, reason=None):
        if not ctx.message.author.guild_permissions.ban_members:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })
            return

        user = await self.ban_helper(ctx, member, action="unban")
        if user is None:
            return
        
        try:
            await ctx.guild.unban(user, reason=reason)
            await cmdhelper.send_message(ctx, {
                "title": "Unban",
                "description": f"Unbanned {user.name}" + (f" for reason: {reason}" if reason else "")
            })
            
        except Exception as e:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"{e}",
                "colour": "ff0000"
            })

    @commands.command(name="kick", description="Kick a member from the command server.", usage="[member] [reason]")
    async def kick(self, ctx, member, *, reason=None):
        if not ctx.message.author.guild_permissions.kick_members:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })
            return
        
        user = None
        
        try:
            if "<@" in member:
                _id = int(member[2:-1])
            else:
                _id = int(member)
                
            user = discord.utils.get(self.bot.users, id=_id)
                
        except Exception as e:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"Failed to find user: {e}",
                "colour": "ff0000"
            })
            
        if user is None:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "Failed to find user.",
                "colour": "ff0000"
            })

        try:
            await ctx.guild.kick(user, reason=reason)
            await cmdhelper.send_message(ctx, {
                "title": "Kick",
                "description": f"Kicked {user.name}" + (f" for reason: {reason}" if reason else "")
            })
            
        except Exception as e:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"{e}",
                "colour": "ff0000"
            })

    @commands.command(name="mute", description="Mute a member.", usage="[member] [length] [reason]", aliases=["timeout"])
    async def mute(self, ctx, member: discord.Member, time: str, *, reason=None):
        if not ctx.message.author.guild_permissions.mute_members:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })
            return

        length = ""

        if time.endswith("s"):
            length = int(time[:-1])

        elif time.endswith("m"):
            length = int(time[:-1]) * 60

        elif time.endswith("h"):
            length = int(time[:-1]) * 60 * 60

        elif time.endswith("d"):
            length = int(time[:-1]) * 60 * 60 * 24

        else:
            length = int(time)

        length = datetime.timedelta(seconds=length)

        await member.timeout(length)
        await cmdhelper.send_message(ctx, {
            "title": "Mute",
            "description": f"Muted {member.name} for {time}" + (f" for reason: {reason}" if reason else "")
        })

    @commands.command(name="unmute", description="Unmute a member.", usage="[member]", aliases=["untimeout"])
    async def unmute(self, ctx, member: discord.Member):
        if not ctx.message.author.guild_permissions.mute_members:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You do not have permission to use this command.",
                "colour": "ff0000"
            })
            return

        await member.timeout(datetime.timedelta(seconds=0))
        await cmdhelper.send_message(ctx, {
            "title": "Unmute",
            "description": f"Unmuted {member.name}"
        })

    @commands.command(name="poll", description="Create a poll.", usage="[question] [options]")
    async def poll(self, ctx, question, *options):
        if len(options) > 10:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You can only have a maximum of 10 options.",
                "colour": "ff0000"
            })

        if len(options) < 2:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You need at least 2 options.",
                "colour": "ff0000"
            })

        description = ""
        for i, option in enumerate(options):
            description += f"{i + 1}. {option}\n"

        msg = await cmdhelper.send_message(ctx, {
            "title": question,
            "description": description
        }, delete_after=10000000)

        for i in range(len(options)):
            await msg.add_reaction(f"{i + 1}\u20e3")

    @commands.command(name="discordpoll", description="Create a poll using discord's poll feature.", usage="[question] [options]")
    async def discordpoll(self, ctx, question, *options):
        if len(options) > 10:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You can only have a maximum of 10 options.",
                "colour": "ff0000"
            })

        if len(options) < 2:
            return await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": "You need at least 2 options.",
                "colour": "ff0000"
            })

        resp = requests.post(f"https://discord.com/api/channels/{ctx.channel.id}/messages", headers={
            "Authorization": f"{self.cfg.get('token')}",
            "Content-Type": "application/json"
        }, json={
            "content": "",
            "poll": {
                "question": {
                    "text": question
                },
                "answers": [
                    {
                        "poll_media": {
                            "text": option
                        }
                    } for option in options
                ],
                "allow_multiselect": False,
                "duration": 24,
                "layout_type": 1
            }
        })

        if resp.status_code != 200:
            await cmdhelper.send_message(ctx, {
                "title": "Error",
                "description": f"Failed to create poll, see console for more information.",
                "colour": "ff0000"
            })

            console.print_error(f"Failed to create poll: {resp.json()}")

        else:
            await cmdhelper.send_message(ctx, {
                "title": "Poll",
                "description": "Poll created."
            })

def setup(bot):
    bot.add_cog(Mod(bot))
