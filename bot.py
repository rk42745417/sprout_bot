import os

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("token")
MY_GUILD = discord.Object(id=int(os.getenv("guild")))

# This intent is required to access member information
intents = discord.Intents.default()
intents.members = True

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')

@client.tree.command()
@app_commands.checks.has_permissions(manage_roles=True)
async def get_ids(interaction: discord.Interaction, role_id: str):
    guild = interaction.guild
    role = guild.get_role(int(role_id))

    if role is None:
        await ctx.send(f"Role with ID '{role_id}' not found.")
        return

    user_names = []
    for member in role.members:
        user_names.append(member.name)

    await interaction.response.send_message('\n'.join(user_names))

client.run(BOT_TOKEN)
