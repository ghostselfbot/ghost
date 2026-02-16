DEFAULT_RPC = {
    "enabled": False,
    "state": "ghost aint dead",
    "state_url": "",
    "details": "",
    "details_url": "",
    "large_image": "https://avatars.githubusercontent.com/u/187971942?s=200&v=4",
    "large_text": "ghostt.cc",
    "large_url": "https://ghostt.cc/",
    "small_image": "",
    "small_text": "",
    "small_url": "",
    "name": "Ghost"
}

DEFAULT_CONFIG = {
    "token": "",
    "prefix": ".",
    "theme": "ghost",
    "apis": {
        "serpapi": ""
    },
    "message_settings": {
        "auto_delete_delay": 15,
        "style": "image"
    },
    "session_spoofing": {
        "enabled": False,
        "device": "desktop"
    },
    "snipers": {
        "nitro": {
            "enabled": True,
            "ignore_invalid": False,
            "webhook": "",
            "name": "nitro"
        },
        "privnote": {
            "enabled": True,
            "ignore_invalid": False,
            "webhook": "",
            "name": "privnote"
        }
    },
    "rich_presence": DEFAULT_RPC
}

DEFAULT_THEME = {
    "title": "ghost selfbot",
    "emoji": "\ud83d\udc7b",
    "image": "https://ghostt.cc/assets/ghost.png",
    "colour": "#575757",
    "footer": "ghost aint dead"
}

DEFAULT_SCRIPT = """
@ghost.command(name="example")
async def example(ctx):
    await ctx.send("Example command")
"""