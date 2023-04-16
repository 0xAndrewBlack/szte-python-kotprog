import os
import random
import discord

from typing import Literal, Union, NamedTuple
from discord import app_commands
from decouple import config
from enum import Enum

BOT_TOKEN = config('DC_BOT_TOKEN')
MY_GUILD = discord.Object(id=config('GUILD_ID', cast=int))


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)

        await self.tree.sync(guild=MY_GUILD)


client = MyClient()


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('-'*50)


@client.tree.command()
@app_commands.describe()
async def roll(interaction: discord.Interaction):
    """Rolls a dice"""

    await interaction.response.send_message(f'You rolled a {random.randint(1, 6)}', ephemeral=True)


@client.tree.command()
@app_commands.describe(first='The first number to add', second='The second number to add')
async def add(interaction: discord.Interaction, first: app_commands.Range[int, 0, 100], second: app_commands.Range[int, 0, None],):
    """Adds two numbers together"""

    await interaction.response.send_message(f'{first} + {second} = {first + second}', ephemeral=True)


@client.tree.command(name='channel-info')
@app_commands.describe(channel='The channel to get info of')
async def channel_info(interaction: discord.Interaction, channel: Union[discord.VoiceChannel, discord.TextChannel]):
    """Shows basic channel info for a text or voice channel."""

    embed = discord.Embed(title='Channel Info')
    embed.add_field(name='Name', value=channel.name, inline=True)
    embed.add_field(name='ID', value=channel.id, inline=True)
    embed.add_field(name='Type', value='Voice' if isinstance(channel, discord.VoiceChannel) else 'Text', inline=True)

    embed.set_footer(text='Created').timestamp = channel.created_at

    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command()
@app_commands.describe(action='The action to do in the shop', item='The target item')
async def shop(interaction: discord.Interaction, action: Literal['Buy', 'Sell'], item: str):
    """Interact with the shop"""

    await interaction.response.send_message(f'Action: {action}\nItem: {item}')


client.run(BOT_TOKEN)
