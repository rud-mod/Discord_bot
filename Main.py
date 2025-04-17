import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

BAD_WORDS = ["badword", "badword2"]
WARN_LIMIT = 4
ADMIN_ROLES = ["Void", "Mod"]
LOG_CHANNEL_ID = 1361012590435897545  # <-- Replace with your log channel ID

warn_file = "warns.json"
if os.path.exists(warn_file):
    with open(warn_file, "r") as f:
        warns = json.load(f)
else:
    warns = {}

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if any(role.name in ADMIN_ROLES for role in message.author.roles):
        return

    content = message.content.lower()
    if any(bad_word in content for bad_word in BAD_WORDS):
        await message.delete()

        user_id = str(message.author.id)
        warns[user_id] = warns.get(user_id, 0) + 1

        with open(warn_file, "w") as f:
            json.dump(warns, f)

        await message.channel.send(f"{message.author.mention}, warning {warns[user_id]}/{WARN_LIMIT}", delete_after=5)

        # Send log message
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"User {message.author} used a bad word in {message.channel.mention}.\n"
                f"Issued warning {warns[user_id]}/{WARN_LIMIT}."
            )

        if warns[user_id] >= WARN_LIMIT:
            try:
                await message.author.timeout(duration=3600, reason="Too many warnings")
                await message.channel.send(f"{message.author.mention} has been timed out.")

                if log_channel:
                    await log_channel.send(
                        f"User {message.author} reached {WARN_LIMIT} warnings and was timed out for 1 hour."
                    )
            except Exception as e:
                print(f"Failed to timeout: {e}")

    await bot.process_commands(message)

bot.run("MTM2MTAxMTg5NDQ5MTY4MDg3OA.GD3i6x.i9reNFK1tvGGbZ6ZZZ_z8HwXJF4qcdytu5iOVQ")
