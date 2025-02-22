import os

import discord
import asyncio
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
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.tree.command()
@app_commands.checks.has_permissions(manage_roles=True)
async def get_ids(interaction: discord.Interaction, role: discord.Role):
    guild = interaction.guild

    if role is None:
        await ctx.send(f"Role not found.")
        return

    user_names = []
    for member in role.members:
        user_names.append(member.name)

    await interaction.response.send_message('\n'.join(user_names))

@client.tree.command()
@app_commands.checks.has_permissions(manage_roles=True)
async def add_roles_to_list(
    interaction: discord.Interaction, role: discord.Role, members: str
):
    await interaction.response.defer()
    
    guild = interaction.guild
    member_ids = [mid.strip() for mid in members.split(',') if len(mid.strip()) > 0]
    
    if not member_ids:
        await interaction.followup.send("No valid member IDs provided.")
        return
    
    try:
        for member_id in member_ids:
            member = guild.get_member_named(member_id)
            if member:
                await member.add_roles(role)
                await asyncio.sleep(1)  # To prevent rate limits
                print(f'Added {role.name} to {member.display_name}')
            else:
                print(f'Member with ID {member_id} not found')
        
        await interaction.followup.send(f'Successfully added {role.name} to given users')
    except discord.Forbidden:
        await interaction.followup.send(
            'Forbidden: added roles must appear lower in the list of roles than the highest role of the bot.'
        )
    except Exception as e:
        print(f'Error: {e}')
        await interaction.followup.send(f'An error occurred: {str(e)}')


@client.tree.command()
@app_commands.checks.has_permissions(manage_roles=True)
async def add_roles_to_everyone(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    guild = interaction.guild

    if role is None:
        await ctx.send(f"Role not found.")
        return

    try:
        for member in guild.members:
            await member.add_roles(role)
            await asyncio.sleep(1)
            print('done, and keep doing...')
        await interaction.followup.send(f'Successfully added {role.name} to all users')
    except discord.Forbidden:
        await interaction.followup.send('Forbidden: added Roles must appear lower in the list of roles than the highest role of the member.')
    except:
        print('error dont know why')
        await interaction.followup.send('Error')

client.run(BOT_TOKEN)
