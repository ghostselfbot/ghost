import os
import re
import json
import asyncio
import discord
import requests

from . import codeblock
from . import imgembed
from utils import webhook
from utils import config

get_command_full_name = lambda cmd: f"{cmd.parent.name} {cmd.name}" if cmd.parent else cmd.name

def format_time(seconds, short_form=True):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes   = divmod(minutes, 60)
    days, hours      = divmod(hours, 24)
    
    seconds = int(seconds)
    minutes = int(minutes)
    hours   = int(hours)
    days    = int(days)

    if days:
        return f"{days}d, {hours}h, {minutes}m" if short_form else f"{days} days, {hours} hours, {minutes} mins"
    elif hours:
        return f"{hours}h, {minutes}m" if short_form else f"{hours} hours, {minutes} mins"
    elif minutes:
        return f"{minutes}m, {seconds}s" if short_form else f"{minutes} mins, {seconds} secs"
    else:
        return f"{seconds}s" if short_form else f"{seconds} seconds"

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Enclosed Characters
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

def cog_desc(cmd, desc):
    return f"{desc}\n{cmd}"

def generate_help_pages(bot, cog_name):
    commands = bot.get_cog(cog_name).walk_commands()
    command_details = []
    max_name_length = 0

    for cmd in commands:
        if cmd.name.lower() != cog_name.lower():
            full_name = get_command_full_name(cmd)
            max_name_length = max(max_name_length, len(full_name))
            command_details.append((full_name, cmd.description))

    formatted_commands = []
    formatted_commands_codeblock = []

    for name, description in command_details:
        padded_name = name.ljust(max_name_length)
        if description.endswith("."):
            description = description[:-1]
        formatted_commands_codeblock.append(f"{padded_name} :: {description}")
        formatted_commands.append(f"**{bot.command_prefix}{name}** {description}")

    def split_into_pages(commands_list, max_length):
        pages = []
        current_page = ""
        for cmd in commands_list:
            if len(current_page) + len(cmd) > max_length:
                pages.append(current_page)
                current_page = ""
            current_page += f"{cmd}\n"
        if current_page:
            pages.append(current_page)
        return pages

    codeblock_pages = split_into_pages(formatted_commands_codeblock, 1000)
    image_pages = split_into_pages(formatted_commands, 400)
    embed_pages = split_into_pages(formatted_commands, 1000)

    return {"codeblock": codeblock_pages, "image": image_pages, "embed": embed_pages}

async def rich_embed(ctx, embed):
    cfg = config.Config()
    webhook_url = cfg.get("rich_embed_webhook")
    webhook_client = webhook.Webhook.from_url(webhook_url)
    webhook_channel = ctx.bot.get_channel(int(webhook_client.channel_id))
    webhook_client.send(embed=embed.to_dict())

    async for message in webhook_channel.history(limit=1):
        await message.ack()
        
        try:
            resp = requests.post(
                f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages", 
                headers={"Authorization": cfg.get("token"), "Content-Type": "application/json"}, 
                data=json.dumps({
                    "content": "",
                    "flags": 0,
                    "message_reference": {
                        "channel_id": message.channel.id,
                        "guild_id": message.guild.id,
                        "message_id": message.id,
                        "type": 1
                    }
                })
            )

            if resp.status_code == 200:
                await asyncio.sleep(cfg.get("message_settings")["auto_delete_delay"])
                try:
                    requests.delete(f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages/{resp.json()['id']}", headers={"Authorization": cfg.get("token")})
                except:
                    pass
        
        except Exception as e:
            print(e)

async def send_message(ctx, embed_obj: dict, extra_title="", extra_message="", delete_after=None):
    cfg = config.Config()
    theme = cfg.theme

    title = embed_obj.get("title", theme.title)
    description = embed_obj.get("description", "")
    colour = embed_obj.get("colour", theme.colour)
    footer = embed_obj.get("footer", theme.footer)
    thumbnail = embed_obj.get("thumbnail", theme.image)
    codeblock_desc = embed_obj.get("codeblock_desc", description)

    if delete_after is None:
        delete_after = cfg.get("message_settings")["auto_delete_delay"]
    elif delete_after is False:
        delete_after = None

    msg_style = cfg.get("message_settings")["style"]
    if msg_style == "embed" and not cfg.get("rich_embed_webhook"):
        msg_style = "codeblock"

    if msg_style == "codeblock":
        description = re.sub(r"[*_~`]", "", codeblock_desc)
        if title == theme.title:
            title = f"{theme.emoji} {title}"

        if len(description.split("\n")) == 1:
            extra_title = description
            description = ""

        msg = await ctx.send(
            str(codeblock.Codeblock(
                title=title,
                description=description,
                extra_title=extra_title,
                # footer=footer
            )),
            delete_after=delete_after
        )

    elif msg_style == "image":
        title = remove_emojis(title.replace(theme.emoji, "").lstrip())
        embed2 = imgembed.Embed(title=title, description=description, colour=colour)
        embed2.set_footer(text=footer)
        embed2.set_thumbnail(url=thumbnail)
        embed_file = embed2.save()

        msg = await ctx.send(file=discord.File(embed_file, filename=embed_file.split("/")[-1]), delete_after=delete_after)
        os.remove(embed_file)

    elif msg_style == "embed" and cfg.get("rich_embed_webhook"):
        if title == theme.title:
            title = f"{theme.emoji} {title}"
        embed = discord.Embed(
            title=title,
            description=description,
            colour=discord.Color.from_str(colour)
        )
        embed.set_footer(text=footer)
        embed.set_thumbnail(url=thumbnail)

        msg = await rich_embed(ctx, embed)

    if extra_message:
        extra_msg = await ctx.send(extra_message, delete_after=delete_after)
        return msg, extra_msg

    return msg

async def send_error_message(ctx, error_text):
    await send_message(ctx, {"title": "Error", "description": error_text, "colour": "#ff0000"})