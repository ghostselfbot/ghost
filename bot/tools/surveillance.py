import asyncio
import discord
import json
import random
from datetime import datetime
from discord.errors import HTTPException

from utils import files
from utils.config import Config

class SurveillanceConsole:
    def __init__(self, controller):
        self.controller = controller
        self.gui = None
        
    def set_gui(self, gui):
        self.gui = gui
        
    def add_log(self, prefix, text):
        self.gui.add_log(prefix, text)

    def success(self, message):
        self.add_log("success", message)
        
    def error(self, message):
        self.add_log("error", message)
        
    def info(self, message):
        self.add_log("info", message)
        
    def warning(self, message):
        self.add_log("warning", message)

class Surveillance:
    def __init__(self, controller):
        self.bot = None
        self.gui = None
        self.controller = controller
        self.cfg = Config()
        self.running = False
        self.mutual_guilds = []
        self.data = {}
        self.semaphore = asyncio.Semaphore(5)
        self.member_id = None
        self.cache = set()
        self.console = SurveillanceConsole(controller)
        self.tasks = []
        self.total_messages = 0
        self.user_total_messages = 0
        
    def set_gui(self, gui):
        self.gui = gui
        self.console.set_gui(gui)
        self.console.success("Surveillance GUI set successfully.")

    def set_bot(self, bot):
        self.bot = bot
        self.load_cache()
        self.console.success("Surveillance bot set successfully.")

    def get_data_path(self):
        return files.get_application_support() + f"/data/surveillance/{self.member_id}.json"

    def save_data(self):
        if not self.data:
            return
        try:
            with open(self.get_data_path(), "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            self.console.error(f"Error saving data: {e}")

    def load_cache(self):
        try:
            with open(self.get_data_path(), "r") as f:
                self.data = json.load(f)
                for guild in self.data.values():
                    for channel_data in guild.values():
                        for msg in channel_data.get("messages", []):
                            if isinstance(msg, dict) and "id" in msg:
                                self.cache.add(msg["id"])
                                self.total_messages += 1
                                self.user_total_messages += 1
                self.console.success(f"Loaded {len(self.cache)} cached messages.")
        except FileNotFoundError:
            self.console.info("No existing cache file found.")
        except Exception as e:
            self.console.error(f"Error loading cache: {e}")
            
        self.update_progress_labels()

    async def get_permissions(self, channel):
        member = await channel.guild.fetch_member(self.member_id)
        member_role = member.top_role
        bot_role = channel.guild.me.top_role
    
        return (
            channel.permissions_for(member).read_messages and 
            channel.permissions_for(channel.guild.me).read_messages or 
            channel.overwrites_for(member_role).read_messages and 
            channel.overwrites_for(bot_role).read_messages 
        )

    async def fetch_context_channel(self, channel):
        try:
            latest_msg = [msg async for msg in channel.history(limit=1)][0]
            context = await self.bot.get_context(latest_msg)
            if context:
                self.console.success(f"Context fetched for channel: {channel.name}")
                return context.channel
        except Exception as e:
            if "429" in str(e):
                self.console.error(f"Rate limit exceeded for channel: {channel.name} - Waiting...")
                await asyncio.sleep(5)
                return await self.fetch_context_channel(channel)
        return None

    def update_progress_labels(self):
        if not self.gui:
            return
        
        if self.total_messages > 0 or self.user_total_messages > 0:
            self.gui._update_progress_labels(self.total_messages, self.user_total_messages)
   
    def add_message(self, guild, channel, message):
        gname, cname = guild.name, channel.name
        if gname not in self.data:
            self.data[gname] = {}
        if cname not in self.data[gname]:
            self.data[gname][cname] = {
                "oldest_timestamp": message.created_at.isoformat(),
                "newest_timestamp": message.created_at.isoformat(),
                "messages": []
            }

        entry = self.data[gname][cname]

        msg_data = {
            "id": message.id,
            "timestamp": message.created_at.isoformat(),
            "content": message.content,
            "attachments": [a.url for a in message.attachments]
        }
        entry["messages"].append(msg_data)
        self.cache.add(message.id)

        ts = message.created_at.isoformat()
        if ts < entry["oldest_timestamp"]:
            entry["oldest_timestamp"] = ts
        if ts > entry["newest_timestamp"]:
            entry["newest_timestamp"] = ts

        self.update_progress_labels()

    async def get_messages(self, channel, delay=.5):
        async with self.semaphore:
            try:
                if not self.running:
                    return
                
                await asyncio.sleep(delay)
                
                self.console.info(f"Fetching messages from channel: {channel.name}")
                channel = await self.fetch_context_channel(channel) or channel
                guild = channel.guild
                
                gname, cname = guild.name, channel.name
                entry = self.data.get(gname, {}).get(cname, {})

                oldest = entry.get("oldest_timestamp")
                newest = entry.get("newest_timestamp")

                # Convert to datetime
                before_dt = datetime.fromisoformat(oldest) if oldest else None
                after_dt = datetime.fromisoformat(newest) if newest else None

                # Fetch newer messages
                if after_dt:
                    async for message in channel.history(limit=None, oldest_first=False, after=after_dt):
                        if int(message.author.id) == int(self.member_id) and message.id not in self.cache:
                            self.add_message(guild, channel, message)
                            self.user_total_messages += 1
                        self.total_messages += 1
                        self.update_progress_labels()

                # Fetch older messages
                if before_dt:
                    async for message in channel.history(limit=None, oldest_first=True, before=before_dt):
                        if int(message.author.id) == int(self.member_id) and message.id not in self.cache:
                            self.add_message(guild, channel, message)
                            self.user_total_messages += 1
                        self.total_messages += 1
                        self.update_progress_labels()

                # If no known timestamps, fetch all
                if not after_dt and not before_dt:
                    async for message in channel.history(limit=None, oldest_first=False):
                        if int(message.author.id) == int(self.member_id) and message.id not in self.cache:
                            self.add_message(guild, channel, message)
                            self.user_total_messages += 1
                        self.total_messages += 1
                        self.update_progress_labels()

            except HTTPException as e:
                if e.status == 429:
                    retry_after = getattr(e, "retry_after", 8)
                    self.console.error(f"Rate limited on {channel.name}. Retrying in {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    return await self.get_messages(channel)
                else:
                    self.console.error(f"HTTP error on {channel.name}: {e}")
            except Exception as e:
                self.console.error(f"Error fetching messages from {channel.guild.name} - {channel.name}: {e}")

    async def attempt_scrape(self, guild, delay=1):
        if not self.running:
            return
        
        for channel in guild.channels:
            if not self.running:
                return
            if isinstance(channel, discord.TextChannel) and await self.get_permissions(channel):
                print(f"Adding task for channel: {channel.name}")
                task = asyncio.create_task(self.get_messages(channel, delay=delay))
                self.tasks.append(task)
                delay += 0.85

    async def get_mutual_guilds(self):
        mutual_guilds = []
        
        for guild in self.bot.guilds:
            try:
                member = await guild.fetch_member(int(self.member_id))
            except Exception as e:
                member = None
            if member:
                mutual_guilds.append(guild)
                self.console.info(f"Found mutual guild: {guild.name} with {len(guild.channels)} channels.")
                
        return mutual_guilds

    def organise_guilds(self):
        self.mutual_guilds.sort(key=lambda g: len(g.members), reverse=True)
        self.mutual_guilds.sort(key=lambda g: g.name.lower())

    async def start(self):
        if self.member_id is None:
            self.console.error("Member ID not set.")
            return

        self.running = True
        self.console.info("Surveillance started.")
        self.mutual_guilds = await self.get_mutual_guilds()
        self.gui._check_surveillance_running()
        self.gui.mutual_guilds = self.mutual_guilds

        if not self.tasks:
            if not self.mutual_guilds:
                self.console.error("No mutual guilds found.")
                await self.stop()
                return

            self.organise_guilds()
            self.load_cache()

            delay = 1
            for guild in self.mutual_guilds:
                if not self.running:
                    return
                await self.attempt_scrape(guild, delay=delay)
                delay += 0.54

            if not self.tasks:
                self.console.error("No tasks created.")
                await self.stop()
                return

        for _ in range(3):
            random.shuffle(self.tasks)
            
        self.console.info(f"Starting {len(self.tasks)} tasks...")
        await asyncio.gather(*self.tasks)

        self.console.success("All tasks completed.")
        await self.stop()

    async def stop(self):
        self.running = False
        
        for task in self.tasks:
            if not task.done():
                task.cancel()
                self.console.warning("Cancelled a running task.")
        self.tasks.clear()
        
        if self.data:
            self.console.info("Saving data...")
            self.save_data()
        
        self.console.success("Surveillance stopped and data saved.")
        self.gui._check_surveillance_running()
        
    def reset(self):
        self.running = False
        self.data = {}
        self.member_id = None
        self.cache.clear()
        self.tasks.clear()
        self.total_messages = 0
        self.user_total_messages = 0
        self.console.info("Surveillance reset. All data cleared and tasks cancelled.")
        self.gui._check_surveillance_running()

    def set_member_id(self, member_id):
        self.member_id = member_id
        self.data = {}
        self.cache.clear()
        self.load_cache()
        self.console.success(f"Member ID set to {self.member_id}. Cache cleared and data loaded.")