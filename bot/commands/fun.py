import discord
import requests
import asyncio
import random
import faker
import datetime
import os

from discord.ext import commands
from utils import config, files
import bot.helpers.cmdhelper as cmdhelper
import bot.helpers.soundboard as soundboard
import bot.helpers.codeblock as codeblock

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cfg = config.Config()
        self.fake = faker.Faker()
        self.description = cmdhelper.cog_desc("fun", "Fun commands")
        self.morse_code = {
            "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
            "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
            "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
            "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
            "Y": "-.--", "Z": "--..", "1": ".----", "2": "..---", "3": "...--",
            "4": "....-", "5": ".....", "6": "-....", "7": "--...", "8": "---..",
            "9": "----.", "0": "-----"
        }

    @commands.command(name="fun", description="Fun commands.", usage="")
    async def fun(self, ctx, selected_page: int = 1):
        cfg = self.cfg
        pages = cmdhelper.generate_help_pages(self.bot, "Fun")

        await cmdhelper.send_message(ctx, {
            "title": f"🏓 fun commands",
            "description": pages[cfg.get("message_settings")["style"]][selected_page - 1 if selected_page - 1 < len(pages[cfg.get("message_settings")["style"]]) else 0],
            "footer": f"Page {selected_page}/{len(pages[cfg.get('message_settings')['style']])}",
            "codeblock_desc": pages["codeblock"][selected_page - 1 if selected_page - 1 < len(pages["codeblock"]) else 0]
        }, extra_title=f"Page {selected_page}/{len(pages['codeblock'])}")

    @commands.command(name="rickroll", description="Never gonna give you up.", usage="")
    async def rickroll(self, ctx):
        lyrics = requests.get("https://gist.githubusercontent.com/bennyscripts/c8f9a62542174cdfb45499fdf8719723/raw/2f6a8245c64c0ea3249814ad8e016ceac45473e0/rickroll.txt").text
        for line in lyrics.splitlines():
            await ctx.send(line)
            await asyncio.sleep(1)

    @commands.command(name="coinflip", description="Flip a coin.", aliases=["cf"])
    async def coinflip(self, ctx):
        sides = ["heads", "tails"]
        msg = await ctx.send("> Flipping the coin...")

        await asyncio.sleep(1)
        await msg.edit(content=f"> The coin landed on `{random.choice(sides)}`!")

    @commands.command(name="iq", description="Get the IQ of a user.", usage="[user]", aliases=["howsmart", "iqrating"])
    async def iq(self, ctx, *, user: discord.User):
        iq = random.randint(45, 135)
        smart_text = ""

        if iq > 90 and iq < 135:
            smart_text = "They're very smart!"
        if iq > 70 and iq < 90:
            smart_text = "They're just below average."
        if iq > 50 and iq < 70:
            smart_text = "They might have some issues."
        elif iq < 50:
            smart_text = "They're severely retarded."

        embed = discord.Embed(title=f"{user.name}'s IQ", description=f"{user.name}'s IQ is {iq}. {smart_text}")
        await cmdhelper.send_message(ctx, embed.to_dict())

    @commands.command(name="howgay", description="Get the gayness of a user.", usage="[user]", aliases=["gay", "gayrating"])
    async def howgay(self, ctx, *, user: discord.User):
        gay_percentage = random.randint(0, 100)

        embed = discord.Embed(title=f"how gay is {user.name}?", description=f"{user.name} is {gay_percentage}% gay!")
        await cmdhelper.send_message(ctx, embed.to_dict())

    @commands.command(name="howblack", description="Get the blackness of a user.", usage="[user]", aliases=["black", "blackrating"])
    async def howblack(self, ctx, *, user: discord.User):
        black_percentage = random.randint(0, 100)

        embed = discord.Embed(title=f"how black is {user.name}?", description=f"{user.name} is {black_percentage}% black!")
        await cmdhelper.send_message(ctx, embed.to_dict())

    @commands.command(name="pp", description="Get the size of a user's dick.", usage="[user]", aliases=["dick", "dicksize", "penis"])
    async def pp(self, ctx, *, user: discord.User):
        penis = "8" + ("=" * random.randint(0, 12)) + "D"
        inches = str(len(penis)) + "\""

        embed = discord.Embed(title=f"{user.name}'s pp size", description=f"{user.name} has a {inches} pp.\n{penis}")
        await cmdhelper.send_message(ctx, embed.to_dict())

    @commands.command(name="rps", description="Play rock paper scissors", usage="")
    async def rps(self, ctx):
        await ctx.send(f"Computer choses `{random.choice(['rock', 'paper', 'scissors'])}`")

    @commands.command(name="slots", description="Play a slot machine.", aliases=["slotmachine", "slot"])
    async def slots(self, ctx):
        emojis_chances = [("🍒", 0.01), ("🍊", 0.02), ("🍎", 0.06), ("💎", 0.08), ("🍆", 0.14), ("🍉", 0.24), ("🎰", 0.36)]
        emojis = []
        reels = ()

        msg = await ctx.send("> Setting up your slot machine...")

        for emoji, chance in emojis_chances:
            emojis += emoji * int(chance * 100)

        await asyncio.sleep(.75)

        for _ in range(8):
            reels = (random.choice(emojis), random.choice(emojis), random.choice(emojis))
            await msg.edit(content=f"> {reels[0]} {reels[1]} {reels[2]}")
            await asyncio.sleep(0.5)

        if reels[0] == reels[1] == reels[2]:
            await msg.edit(content=f"> {reels[0]} {reels[1]} {reels[2]}\n> You won!")
        else:
            await msg.edit(content=f"> {reels[0]} {reels[1]} {reels[2]}\n> You lost!")

    @commands.command(name="encodemorsecode", description="Encode text to morse code.", usage="[text]", aliases=["morsecode"])
    async def encodemorse(self, ctx, *, text: str):
        morse = ""
        for char in text:
            if char.upper() in self.morse_code:
                morse += self.morse_code[char.upper()] + " "
            else:
                morse += " "

        await ctx.send(morse)

    @commands.command(name="decodemorsecode", description="Decode morse code to text.", usage="[morse]", aliases=["morsecodedecode"])
    async def decodemorse(self, ctx, *, morse: str):
        text = ""
        morse_code = {value: key for key, value in self.morse_code.items()}
        for char in morse.split(" "):
            if char in morse_code:
                text += morse_code[char]
            else:
                text += " "
        await ctx.send(text)

    @commands.command(name="blocksend", description="Send a message to a blocked user.", usage="[user] [message]")
    async def blocksend(self, ctx, user: discord.User, *, message: str):
        await user.unblock()
        await user.send(message)
        await user.block()

        embed = discord.Embed(title=f"block send", description=f"Sent a message to {user.name} ({user.id}).\n**Message:** {message}")
        await cmdhelper.send_message(ctx, embed_obj=embed.to_dict())

    def get_formatted_items(self, json_obj, tabs=0):
        formatted = ""
        sub_items_count = 0

        for item in json_obj:
            if isinstance(json_obj[item], dict):
                sub_items_count += 1 + tabs
                formatted += ("\t" * tabs) + f"{item}:\n"
                formatted += self.get_formatted_items(json_obj[item], sub_items_count)
                sub_items_count = 0
            else:
                formatted += ("\t" * tabs) + f"{item}: {json_obj[item]}\n"

        return formatted

    @commands.command(name="randomdata", description="Generate random data.", usage="[type]")
    async def randomdata(self, ctx, type_name: str = "unknown"):
        url = ""
        types = [{"name": "businesscreditcard", "url": "https://random-data-api.com/api/business_credit_card/random_card"},
            {"name": "cryptocoin", "url": "https://random-data-api.com/api/crypto_coin/random_crypto_coin"},
            {"name": "hipster", "url": "https://random-data-api.com/api/hipster/random_hipster_stuff"},
            {"name": "google", "url": "https://random-data-api.com/api/omniauth/google_get"},
            {"name": "facebook", "url": "https://random-data-api.com/api/omniauth/facebook_get"},
            {"name": "twitter", "url": "https://random-data-api.com/api/omniauth/twitter_get"},
            {"name": "linkedin", "url": "https://random-data-api.com/api/omniauth/linkedin_get"},
            {"name": "github", "url": "https://random-data-api.com/api/omniauth/github_get"},
            {"name": "apple", "url": "https://random-data-api.com/api/omniauth/apple_get"}]

        for _type in types:
            if type_name == _type["name"]:
                url = _type["url"]
                break
            else:
                url = "unknown"

        if url == "unknown":
            await ctx.send(str(codeblock.Codeblock("error", extra_title="Unkown data type.", description="The current types are: " + ", ".join([_type["name"] for _type in types]))))
            return

        resp = requests.get(url)

        if resp.status_code == 200:
            data = resp.json()
            formatted = self.get_formatted_items(data)

            msg = codeblock.Codeblock("random data", extra_title=f"Random {type_name}", description=formatted, style="yaml")
            await ctx.send(str(msg))
        else:
            await ctx.send(str(codeblock.Codeblock("error", extra_title="Failed to get data.")))

    @commands.command(name="kanye", description="Random kanye quote.", usage="")
    async def kanye(self, ctx):
        resp = requests.get("https://api.kanye.rest/")

        if resp.status_code == 200:
            data = resp.json()
            embed = discord.Embed(title=f"Kanye Quote", description=data["quote"])

        else:
            embed = discord.Embed(title="Error", description="Failed to get Kanye quote.")

        await cmdhelper.send_message(ctx, embed.to_dict())

    @commands.command(name="socialcredit", description="Get a user's social credit score.", usage="[user]", aliases=["socialcreditscore", "socialcreditrating", "socialcredits", "socialrating", "socialscore"])
    async def socialcredit(self, ctx, *, user: discord.User):
        score = random.randint(-5000000, 10000000)

        embed = discord.Embed(title=f"Social Credit", description=f"{user.name}'s social credit score is {score}.")
        await cmdhelper.send_message(ctx, embed.to_dict())

    @commands.command(name="dice", description="Roll a dice with a specific side count.", usage="[sides]", aliases=["roll"])
    async def dice(self, ctx, sides: int = 6):
        number = random.randint(1, sides)

        embed = discord.Embed(title=f"{sides} side dice", description=f"You rolled a {number}.")
        await cmdhelper.send_message(ctx, embed.to_dict())

    @commands.command(name="rainbow", description="Create rainbow text.", usage="[text]", aliases=["rainbowtext"])
    async def rainbow(self, ctx, *, text: str):
        colours = [
            "\u001b[1;31m{TEXT}\u001b[0;0m",
            "\u001b[1;33m{TEXT}\u001b[0;0m",
            "\u001b[1;32m{TEXT}\u001b[0;0m",
            "\u001b[1;36m{TEXT}\u001b[0;0m",
            "\u001b[1;34m{TEXT}\u001b[0;0m",
            "\u001b[1;36m{TEXT}\u001b[0;0m",
            "\u001b[1;32m{TEXT}\u001b[0;0m",
            "\u001b[1;33m{TEXT}\u001b[0;0m",
            "\u001b[1;31m{TEXT}\u001b[0;0m"
        ]

        message = await ctx.send(text)

        for _ in range(5):
            for colour in colours:
                await message.edit(f"> ```ansi\n> {colour.replace('{TEXT}', text)}```")
                await asyncio.sleep(.5)

    @commands.command(name="rainbowreact", description="Create a rainbow reaction", usage="[msg id]")
    async def rainbowreact(self, ctx, *, msg_id: int):
        emojis = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
        message = await ctx.fetch_message(msg_id)

        if isinstance(message.channel, discord.DMChannel):
            return await cmdhelper.send_message(ctx, {
                    "title": "Error",
                    "description": "You can't use this command in a DM."
            })

        await message.add_reaction("🫡")

        for _ in range(5):
            for emoji in emojis:
                reaction = await message.add_reaction(emoji)
                await asyncio.sleep(0.25)
                await message.clear_reaction(emoji)

        await message.clear_reaction("🫡")

    def calculate_age(self, born):
        today = datetime.date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @commands.command(name="dox", description="Dox a user.", usage="[user]")
    async def dox(self, ctx, *, user: discord.User):
        name = self.fake.name()
        email = name.lower().split(" ")[0][:random.randint(3, 5)] + "." + name.lower().split(" ")[1] + str(random.randint(10, 99)) + random.choice(["@gmail.com", "@yahoo.com", "@hotmail.com", "@outlook.com"])
        dob = datetime.date(random.randint(1982, 2010), random.randint(1, 12), random.randint(1, 28))
        age = self.calculate_age(dob)
        phone = f"+1 ({random.randint(100, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"

        address_resp = requests.post("https://randommer.io/random-address", data={"number": "1", "culture": "en_US"}, headers={"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"})
        address = address_resp.json()[0]

        info = {
            "Name": name,
            "Email": email,
            "Date of birth": dob.strftime("%d/%m/%Y"),
            "Current age": f"{age} years old",
            "Phone number": phone,
            "Address": address
        }

        longest_key = max([len(key) for key in info])

        await cmdhelper.send_message(ctx, {
            "title": "Dox",
            "description": "\n".join([f"**{key}:** {value}" for key, value in info.items()]),
            "codeblock_desc": "\n".join([f"{key}{' ' * (longest_key - len(key))} :: {value}" for key, value in info.items()])
        }, extra_title=f"{user.name}'s dox")

    @commands.command(name="meme", description="Gets a random meme.", aliases=["getmeme", "randommeme"], usage="")
    async def meme(self, ctx):
        r = requests.get("https://www.reddit.com/r/memes.json?sort=top&t=week", headers={"User-agent": "Mozilla/5.0"})

        if (r.status_code == 429):
            embed = discord.Embed(title="Error", description="Too many requests, please try again later.")
            await cmdhelper.send_message(ctx, embed.to_dict())
            return

        meme = random.choice(r.json()["data"]["children"])["data"]["url"]
        await ctx.send(meme)

    @commands.command(name="dadjoke", description="Get a dad joke.", usage="")
    async def dadjoke(self, ctx):
        r = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
        joke = r.json()["joke"]
        await ctx.send(joke)

    @commands.command(name="insult", description="Get a random insult.", usage="")
    async def insult(self, ctx):
        r = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
        insult = r.json()["insult"]
        await ctx.send(insult)

    @commands.command(name="compliment", description="Get a random compliment.", usage="")
    async def compliment(self, ctx):
        r = requests.get("https://8768zwfurd.execute-api.us-east-1.amazonaws.com/v1/compliments")
        await ctx.send(r.content.replace(b'"', b'').decode("utf-8"))

    @commands.command(name="catfact", description="Get a random cat fact.", usage="")
    async def catfact(self, ctx):
        r = requests.get("https://catfact.ninja/fact")
        fact = r.json()["fact"]
        await ctx.send(fact)

    @commands.command(name="yomomma", description="Get a yo momma joke.", usage="")
    async def yomomma(self, ctx):
        r = requests.get("https://www.yomama-jokes.com/api/v1/jokes/random/")
        joke = r.json()["joke"]
        await ctx.send(joke)

    @commands.command(name="8ball", description="Ask the magic 8ball a question.", usage="[question]", aliases=["magic8ball", "ask8ball"])
    async def eightball(self, ctx, *, question: str):
        responses = ["It is certain", "It is decidedly so", "Without a doubt", "Yes definitely", "You may rely on it",
            "As I see it, yes", "Most likely", "Outlook good", "Yes", "Signs point to yes", "Reply hazy try again",
            "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
            "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]

        await cmdhelper.send_message(ctx, {
            "title": question,
            "description": random.choice(responses)
        })

    @commands.command(name="fakenitro", description="Fake a nitro gift.", usage="")
    async def fakenitro(self, ctx):
        await ctx.send("https://discord.gift/" + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=16)))

    @commands.command(name="hyperlink", description="Create a hyperlink", usage="[link] [text]", aliases=["hyperl"])
    async def hyperlink(self, ctx, link: str, *, text: str):
        await ctx.send(f"[{text}]({link})")

    @commands.command(name="aura", description="Check a user's aura.", usage="[user]", aliases=["karma"])
    async def aura(self, ctx, *, user: discord.User = None):
        if user is None:
            user = ctx.author

        score = random.randint(-100, 100)
        tiers = [((-100, -75), "terrible"), ((-75, -50), "bad"), ((-50, -25), "mild"), ((-25, 0), "okay"), ((0, 25), "good"), ((25, 50), "better"), ((50, 75), "great"), ((75, 100), "amazing")]
        responses = requests.get("https://gist.githubusercontent.com/bennyscripts/d5d3f9007a39ed8254d80039a1fadb52/raw/c670914ee8a1dded4e6f2ec468827b5d807c3f52/karma_responses.json").json()
        chosen_tier = "terrible"
        for (low, high), tier in tiers:
            if low <= score < high:
                chosen_tier = tier

        response = random.choice(responses[chosen_tier])
        await ctx.send(f"{'You have' if user == ctx.author else user.name + ' has'} {score} {ctx.invoked_with}. {response}")

    @commands.command(name="gyatt", description="See if they've got GYATTT", usage="[user]", aliases=["gyat"])
    async def gyatt(self, ctx, *, user: discord.User = None):
        if user is None:
            user = ctx.author

        score = random.randint(0, 10)
        tiers = [((1, 3), "flat"), ((3, 5), "small"), ((5, 7), "big"), ((7, 8), "large"), ((8, 10), "massive")]
        categories = {
                "flat": {
                        "gifs": [
                                "https://tenor.com/view/butt-gif-11020650",
                                "https://tenor.com/view/taylor-swift-concert-sing-hip-shake-live-gif-4844274",
                                "https://tenor.com/view/no-ass-cant-twerk-twerk-gif-9749101",
                                "https://tenor.com/view/your-butts-flat-ellen-how-i-met-your-father-you-have-a-flat-butt-you-didnt-have-a-fat-butt-gif-27469695",

                        ],
                        "responses": [
                            "Bro's butt is flatter than my Wi-Fi connection 😭",
                            "Bro, that’s flatter than my pancake this morning.",
                            "You sure you're not just missing your butt cheeks?",
                            "Not much to work with here, is there?",
                            "That’s less of a butt and more of a speed bump.",
                            "Did you forget to pack your backside today?"
                        ]
                },
                "small": {
                        "gifs": [
                                "https://tenor.com/view/notting-hill-spike-piktroll-nice-firm-buttocks-gif-21660289",
                                "https://tenor.com/view/nojuu-gif-20251727"
                        ],
                        "responses": [
                            "It's there... barely, but it's there.",
                            "Cute little thing you got there, like a button.",
                            "Okay, so you’ve got a butt, but it’s on the shy side.",
                            "Not bad, but it’s still in the ‘just starting’ stage.",
                            "It’s like a snack, but I need a meal 🍑",
                            "That's a nice start, just a few more squats away!"
                        ]
                },
                "big": {
                        "gifs": [
                                "https://media.discordapp.net/attachments/1072589399142973451/1162537084775571496/itsy.gif?ex=678b94c7&is=678a4347&hm=5d2821898b16b48466a9d8c9ea13b9a96431b64eead8eb8e5888f32d55278c28&",
                                "https://tenor.com/view/dog-toy-twerk-what-butt-gif-4580835"
                        ],
                        "responses": [
                            "Now that’s what I call a proper package! 🫢",
                            "Bro, you’re making people turn heads with that!",
                            "I’m here for it. That’s a full-on masterpiece.",
                            "You got some serious cake back there.",
                            "You can feel the power in that booty.",
                            "That’s a whole mood right there, I see you!"
                        ]
                },
                "large": {
                        "gifs": [
                                "https://tenor.com/view/leslie-jordan-leslie-belly-dancing-belly-dance-dancing-gif-25526487",
                                "https://tenor.com/view/nervous-gif-8791067696346074845",
                                "https://tenor.com/view/deadpool-gif-6146788853958018304",
                                "https://tenor.com/view/danse-dance-sexy-girl-black-gif-21636293"
                        ],
                        "responses": [
                                "Oh lord have mercy bro has GYATTT",
                                "Bro is packing some serious gyatt :flushed:",
                                "nah man that is wild...",
                                "i think i broke my neck",
                                "😳🫨😫🥵"
                        ]
                },
                "massive": {
                        "gifs": [
                                "https://tenor.com/view/yes-lawdd-butt-ass-walking-gif-16073853",
                                "https://tenor.com/view/saturday-thicc-male-ass-glutes-gif-9253491003307436413",
                                "https://tenor.com/view/muscle-bodybuilder-pecs-black-pec-bounce-gif-1076301405568312554"

                        ],
                        "responses": [
                                "sit on my face :flushed:",
                                "im weak bro wow",
                                "my legs dont seem to function anymore"
                        ]
                }
        }

        chosen_tier = "small"
        for (low, high), tier in tiers:
            if low <= score < high:
                chosen_tier = tier

        gif = random.choice(categories[chosen_tier]["gifs"])
        response = random.choice(categories[chosen_tier]["responses"])

        await ctx.send(f"{user.mention} {response}")
        await ctx.send(gif)

    @commands.command(name="playsound", description="Play a 5 second sound.", usage="[mp3_url]")
    async def playsound(self, ctx, mp3_url = None):
        cfg = self.cfg
        voice_state = ctx.author.voice
        
        if len(ctx.message.attachments) > 0 and mp3_url is None:
            mp3_url = ctx.message.attachments[0].url

        if not ctx.author.guild_permissions.administrator:
            await cmdhelper.send_message(ctx, {
                "title": "Play Sound",
                "description": f"Admin is required for this command to work",
                "colour": "#ff0000"
            })
            return

        if not voice_state:
            await cmdhelper.send_message(ctx, {
                "title": "Play Sound",
                "description": f"You're not in a voice channel",
                "colour": "#ff0000"
            })
            return

        # if not str(mp3_url).endswith("mp3"):
        #     await cmdhelper.send_message(ctx, {
        #         "title": "Play Sound",
        #         "description": f"That file is not an MP3",
        #         "colour": "#ff0000"
        #     })
        #     return

        sound_res = requests.get(mp3_url)
        if sound_res.status_code != 200:
            await cmdhelper.send_message(ctx, {
                "title": "Play Sound",
                "description": f"404 file not found",
                "colour": "#ff0000"
            })
            return

        with open(files.get_cache_path() + "/mysound.mp3", "wb") as sound_file:
            sound_file.write(sound_res.content)

        soundeffects = soundboard.Soundboard(cfg.get("token"), ctx.guild.id, voice_state.channel.id)
        sound = soundeffects.upload_sound(files.get_cache_path() + "/mysound.mp3", "ghost_sound_player", volume=1, emoji_id=None)

        if sound.id:
            await cmdhelper.send_message(ctx, {
                "title": "Play Sound",
                "description": f"Sound file is being played"
            })

            soundeffects.play_sound(sound.id, source_guild_id=ctx.guild.id)
            soundeffects.delete_sound(sound.id)
            os.remove(files.get_cache_path() + "/mysound.mp3")

        else:
            await cmdhelper.send_message(ctx, {
                "title": "Play Sound",
                "description": f"Sound could not be played. Possible reasons include:\n- File is too long\n- File is over 512KB",
                "colour": "#ff0000"
            })
            return

def setup(bot):
    bot.add_cog(Fun(bot))
