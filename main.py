import discord
from discord.ext import commands
import groq
from flask import Flask
from threading import Thread
import os
import re
from collections import defaultdict
import datetime

# --------------------------
# LOAD SECRETS FROM ENVIRONMENT VARIABLES
# These will be set inside Render dashboard
# --------------------------
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------------------------
# FLASK APP - Keeps bot alive 24/7 on Render
# --------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running and active!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Start Flask server in background
server = Thread(target=run_flask)
server.start()

# --------------------------
# DISCORD BOT SETUP
# --------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.bans = True
intents.kick_members = True
intents.manage_messages = True
intents.manage_roles = True
intents.manage_channels = True
intents.manage_guild = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Initialize Groq AI client
groq_client = groq.Client(api_key=GROQ_API_KEY)

# --------------------------
# CONFIGURATION
# --------------------------
# Anti-Spam Settings
spam_data = defaultdict(list)
SPAM_MESSAGE_LIMIT = 5
SPAM_TIME_WINDOW = 5  # seconds

# Anti-Link Settings
LINK_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
ALLOWED_ROLES = []  # Add role IDs here

# Auto-Moderation Settings
BANNED_WORDS = [
    "badword1", "badword2", "offensiveterm"
]

# Warning System Settings
user_warnings = defaultdict(int)
MAX_WARNINGS = 3
WARNING_DURATION = 7 * 24 * 60 * 60  # 7 days in seconds

# --------------------------
# BOT EVENTS
# --------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("🔧 Auto-Moderation, Anti-Spam, Anti-Link, Warning System & AI Management are active")
    print("------")
    await bot.change_presence(status=discord.Status.invisible, activity=None)

# --------------------------
# CORE MODERATION SYSTEMS
# --------------------------
@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return

    has_bypass_perm = any(role.id in ALLOWED_ROLES for role in message.author.roles)

    # --- Anti-Link ---
    if LINK_REGEX.search(message.content) and not has_bypass_perm:
        user_warnings[message.author.id] += 1
        try:
            await message.delete()
            try:
                await message.author.send(f"⚠️ WARNING {user_warnings[message.author.id]}/{MAX_WARNINGS}:\nYou are not allowed to send links in this server. Further violations will result in action.")
            except:
                pass

            if user_warnings[message.author.id] >= MAX_WARNINGS:
                await message.author.timeout_for(duration=datetime.timedelta(minutes=30), reason="Reached max warnings - Unauthorized links")
                user_warnings[message.author.id] = 0
        except:
            pass

    # --- Anti-Spam ---
    current_time = datetime.datetime.now().timestamp()
    user_timestamps = spam_data[message.author.id]
    user_timestamps.append(current_time)
    spam_data[message.author.id] = [t for t in user_timestamps if current_time - t <= SPAM_TIME_WINDOW]

    if len(spam_data[message.author.id]) > SPAM_MESSAGE_LIMIT and not has_bypass_perm:
        user_warnings[message.author.id] += 1
        try:
            await message.channel.purge(limit=SPAM_MESSAGE_LIMIT + 1, check=lambda m: m.author == message.author)
            try:
                await message.author.send(f"⚠️ WARNING {user_warnings[message.author.id]}/{MAX_WARNINGS}:\nSpamming is not allowed. Please slow down.")
            except:
                pass

            if user_warnings[message.author.id] >= MAX_WARNINGS:
                await message.author.timeout_for(duration=datetime.timedelta(hours=2), reason="Reached max warnings - Spamming")
                user_warnings[message.author.id] = 0
        except:
            pass

    # --- Bad Words Filter ---
    message_content = message.content.lower()
    for word in BANNED_WORDS:
        if word in message_content and not has_bypass_perm:
            user_warnings[message.author.id] += 1
            try:
                await message.delete()
                try:
                    await message.author.send(f"⚠️ WARNING {user_warnings[message.author.id]}/{MAX_WARNINGS}:\nInappropriate language is not allowed here.")
                except:
                    pass

                if user_warnings[message.author.id] >= MAX_WARNINGS:
                    await message.author.timeout_for(duration=datetime.timedelta(hours=1), reason="Reached max warnings - Bad language")
                    user_warnings[message.author.id] = 0
            except:
                break

    # --- Groq AI Analysis ---
    try:
        ai_analysis = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Analyze the given message. Classify it as: SAFE, SPAM, LINK, INAPPROPRIATE, or DANGEROUS. Reply only with the exact classification word."},
                {"role": "user", "content": message.content}
            ],
            temperature=0.1
        )
        classification = ai_analysis.choices[0].message.content.strip()

        if classification == "SPAM" and not has_bypass_perm:
            user_warnings[message.author.id] += 1
            await message.channel.purge(limit=SPAM_MESSAGE_LIMIT + 1, check=lambda m: m.author == message.author)
            try:
                await message.author.send(f"⚠️ WARNING {user_warnings[message.author.id]}/{MAX_WARNINGS}:\nAI detected spam behavior.")
            except:
                pass
            if user_warnings[message.author.id] >= MAX_WARNINGS:
                await message.author.timeout_for(duration=datetime.timedelta(hours=2), reason="Reached max warnings - AI detected spam")
                user_warnings[message.author.id] = 0

        elif classification == "LINK" and not has_bypass_perm:
            user_warnings[message.author.id] += 1
            await message.delete()
            try:
                await message.author.send(f"⚠️ WARNING {user_warnings[message.author.id]}/{MAX_WARNINGS}:\nAI detected unauthorized link.")
            except:
                pass
            if user_warnings[message.author.id] >= MAX_WARNINGS:
                await message.author.timeout_for(duration=datetime.timedelta(minutes=30), reason="Reached max warnings - AI detected link")
                user_warnings[message.author.id] = 0

        elif classification in ["INAPPROPRIATE", "DANGEROUS"] and not has_bypass_perm:
            user_warnings[message.author.id] += 1
            await message.delete()
            try:
                await message.author.send(f"⚠️ WARNING {user_warnings[message.author.id]}/{MAX_WARNINGS}:\nAI detected {classification.lower()} content.")
            except:
                pass
            if user_warnings[message.author.id] >= MAX_WARNINGS:
                duration = datetime.timedelta(days=1) if classification == "DANGEROUS" else datetime.timedelta(hours=3)
                await message.author.timeout_for(duration=duration, reason=f"Reached max warnings - AI detected {classification.lower()} content")
                user_warnings[message.author.id] = 0
    except:
        pass

    # Remove expired warnings
    current_time = datetime.datetime.now().timestamp()
    for user_id in list(user_warnings.keys()):
        if current_time - spam_data[user_id][-1] > WARNING_DURATION:
            user_warnings[user_id] = 0

    await bot.process_commands(message)

# --------------------------
# SERVER MANAGEMENT COMMANDS
# --------------------------
@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "Violated server rules"):
    if member == ctx.author or member.top_role >= ctx.author.top_role:
        return

    user_warnings[member.id] += 1
    try:
        try:
            await member.send(f"⚠️ WARNING {user_warnings[member.id]}/{MAX_WARNINGS}:\nYou are being warned. Continued rule breaks will result in kick.\nReason: {reason}")
        except:
            pass

        if user_warnings[member.id] >= MAX_WARNINGS:
            await member.kick(reason=reason)
            user_warnings[member.id] = 0
    except:
        pass

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "Severe violation of server rules"):
    if member == ctx.author or member.top_role >= ctx.author.top_role:
        return

    user_warnings[member.id] += 1
    try:
        try:
            await member.send(f"⚠️ WARNING {user_warnings[member.id]}/{MAX_WARNINGS}:\nYou are being warned. Continued rule breaks will result in ban.\nReason: {reason}")
        except:
            pass

        if user_warnings[member.id] >= MAX_WARNINGS:
            await member.ban(reason=reason)
            user_warnings[member.id] = 0
    except:
        pass

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    try:
        await ctx.channel.purge(limit=amount)
    except:
        pass

@bot.command(name="setname")
@commands.has_permissions(manage_guild=True)
async def setname(ctx, *, new_name: str):
    try:
        await ctx.guild.edit(name=new_name)
    except:
        pass

@bot.command(name="createrole")
@commands.has_permissions(manage_roles=True)
async def createrole(ctx, role_name: str, color: str = "grey"):
    try:
        role_color = discord.Color(int(color.lstrip('#'), 16)) if color.startswith('#') else getattr(discord.Color, color, discord.Color.default())
        await ctx.guild.create_role(name=role_name, color=role_color)
    except:
        pass

@bot.command(name="assignrole")
@commands.has_permissions(manage_roles=True)
async def assignrole(ctx, member: discord.Member, role: discord.Role):
    if role < ctx.me.top_role:
        try:
            await member.add_roles(role)
        except:
            pass

@bot.command(name="removerole")
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    if role < ctx.me.top_role:
        try:
            await member.remove_roles(role)
        except:
            pass

@bot.command(name="createchannel")
@commands.has_permissions(manage_channels=True)
async def createchannel(ctx, channel_name: str, channel_type: str = "text"):
    try:
        if channel_type.lower() == "voice":
            await ctx.guild.create_voice_channel(name=channel_name)
        else:
            await ctx.guild.create_text_channel(name=channel_name)
    except:
        pass

@bot.command(name="deletechannel")
@commands.has_permissions(manage_channels=True)
async def deletechannel(ctx, channel: discord.TextChannel | discord.VoiceChannel):
    try:
        await channel.delete()
    except:
        pass

@bot.command(name="check")
@commands.has_permissions(manage_messages=True)
async def check_content(ctx, *, content: str):
    try:
        groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "Analyze this content and tell me if it is SAFE, SPAM, contains UNAUTHORIZED LINK, or INAPPROPRIATE. Reply only with the result."},
                {"role": "user", "content": content}
            ],
            temperature=0.1
        )
    except:
        pass

# --------------------------
# RUN BOT
# --------------------------
bot.run(DISCORD_BOT_TOKEN)
    
