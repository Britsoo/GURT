import os
import discord
from discord.ext import commands
import yt_dlp
import re
from flask import Flask
from threading import Thread

# ==== CONFIG ====
PREFIX = "yo."
TARGET_USER_ID = 1282767608806117530
CONTROLLER_ID = 1060214630326214737
AUTO_MESSAGE = "Sorry, he's currently beating the living fuck out of Cathy, he will be back soon!."
# =================

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ==== KEEP-ALIVE SERVER ====
app = Flask('')


@app.route('/')
def home():
    return "Bot is alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


Thread(target=run).start()
# ===========================


# ==== EVENTS ====
@bot.event
async def on_ready():
    print(f"✅ Bot online as {bot.user}")


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot:
        return

    if re.search(r"\byo\b", message.content.lower()):
        await message.channel.send("gurt")
        return

    if message.author.id == CONTROLLER_ID and message.content.startswith(
            f"{PREFIX}say "):
        text = message.content[len(f"{PREFIX}say "):].strip()
        if text:
            await message.channel.send(text)
        try:
            await message.delete()
        except discord.Forbidden:
            print("❌ Bot can't delete messages in this channel.")
        except discord.NotFound:
            pass
        return

    if message.reference and TARGET_USER_ID not in message.raw_mentions:
        return

    if TARGET_USER_ID in message.raw_mentions:
        member = message.guild.get_member(TARGET_USER_ID)
        if member is None:
            try:
                member = await message.guild.fetch_member(TARGET_USER_ID)
            except discord.NotFound:
                member = None

        if member and str(member.status) == "offline":
            await message.channel.send(AUTO_MESSAGE)


# ==== MUSIC COMMANDS ====
@bot.command()
async def join(ctx):
    """Joins the voice channel you're in"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Gurt joined **{channel.name}**!")
    else:
        await ctx.send("Join a VC so this could work on me.")


@bot.command()
async def leave(ctx):
    """Leaves the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("See you, gurt's out.")
    else:
        await ctx.send("I'm not in a voice channel bro.")


@bot.command()
async def play(ctx, *, url):
    """Plays audio from a YouTube link"""
    if not ctx.author.voice:
        await ctx.send("You're not in a voice channel man.")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    YDL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': False
    }

    FFMPEG_OPTIONS = {
        'before_options':
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'Unknown title')

        vc = ctx.voice_client
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))
        await ctx.send(f"Now playing whatever song you pick: **{title}**")

    except Exception as e:
        await ctx.send(f"OMG GURT GURT Malfunction happening: `{e}`")


@bot.command()
async def stop(ctx):
    """Stops playback"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹Alright bet, music is stopped. I'll wait")
    else:
        await ctx.send("Nothing's playing bro.")


# =========================

# Get token from Replit secret
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("❌ ERROR: Missing DISCORD_TOKEN environment variable.")
else:
    bot.run(TOKEN)
