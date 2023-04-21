import os
import random
import discord
import logging
from datetime import datetime

from typing import Literal, Union, NamedTuple
from discord import app_commands
from decouple import config
from prisma import Prisma

BOT_TOKEN = config('DC_BOT_TOKEN')
MY_GUILD = discord.Object(id=config('GUILD_ID', cast=int))

discord.utils.setup_logging()

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logger = logging.getLogger('discord')

logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.DEBUG)


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)

        await self.tree.sync(guild=MY_GUILD)

    async def getMarketplaceItem(self, item_id):
        prisma = Prisma()
        await prisma.connect()

        item = await prisma.marketplace.find_unique(where={"id": item_id})

        return item

    async def getMarketplaceItems(self, page=1, limit=10):
        prisma = Prisma()
        await prisma.connect()

        items = await prisma.marketplace.find_many(skip=(page - 1) * limit, take=limit)

        return items

    async def addMarketplaceItem(self, item, description, seller_id, action, price, currency, message_id):
        prisma = Prisma()
        await prisma.connect()

        item = await prisma.marketplace.create(
            data={
                "actor": str(seller_id),
                "name": item,
                "description": description,
                "price": price,
                "listing": str(action).upper(),
                "currency": currency,
                "message_id": str(message_id),
            }
        )

        return item

    async def deleteMarketplaceItem(self, item_id, seller_id):
        prisma = Prisma()
        await prisma.connect()

        query = await prisma.marketplace.find_unique(where={"id": item_id})
        if query.actor != str(seller_id):
            return None

        item = await prisma.marketplace.update(
            where={
                "id": int(item_id),
            },
            data={
                "status": "sold",
                "deleted_at": datetime.now(),
            }
        )

        return item

    async def updateMarketplaceItem(self, item_id, item, description, seller_id, action, price, currency, message_id):
        prisma = Prisma()
        await prisma.connect()

        query = await prisma.marketplace.find_unique(where={"id": item_id})

        if query.actor != str(seller_id):
            return None

        item = await prisma.marketplace.update(
            where={
                "id": int(item_id),
            },
            data={
                "name": item,
                "description": description,
                "price": price,
                "listing": str(action).upper(),
                "currency": currency,
                "message_id": str(message_id),
            }
        )

        return item


client = MyClient()


@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logger.info('-' * 50)


@client.tree.command(name='roll', description='Rolls the dice')
@app_commands.describe()
async def roll(interaction: discord.Interaction):
    """Rolls a dice"""

    await interaction.response.send_message(f'You rolled a {random.randint(1, 6)}', ephemeral=True)


@client.tree.command(name='channel-info', description='Shows basic channel info for a text or voice channel')
@app_commands.describe(channel='The channel to get info of')
async def channel_info(interaction: discord.Interaction, channel: Union[discord.VoiceChannel, discord.TextChannel]):
    """Shows basic channel info for a text or voice channel."""

    embed = discord.Embed(title='Channel Info')
    embed.add_field(name='Name', value=channel.name, inline=True)
    embed.add_field(name='ID', value=channel.id, inline=True)
    embed.add_field(name='Type', value='Voice' if isinstance(
        channel, discord.VoiceChannel) else 'Text', inline=True)

    embed.set_footer(text='Created').timestamp = channel.created_at

    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name='marketplace', description='Shows the marketplace items')
@app_commands.describe()
async def marketplace(interaction: discord.Interaction, page: app_commands.Range[int, 1, None] = 1, limit: app_commands.Range[int, 1, 10] = 10):
    """Shows the marketplace items"""

    items = await client.getMarketplaceItems(page, limit)

    logger.info(f"Marketplace items queried: {len(items)}")

    embed = discord.Embed(title='Marketplace - Available Listings')

    if (len(items) == 0):
        embed.description = '```There are no items in the marketplace```'

    for item in items:
        embed.add_field(name=f"`{item.id}`", value=f"{str(item.listing).lower().capitalize()} order for `{item.name}` by <@{item.actor}> for `{item.price}{item.currency}`", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name='shop', description='Interact with the shop')
@app_commands.describe(action='The action to do in the shop', item='The target item')
async def shop(interaction: discord.Interaction, action: Literal['Buy', 'Sell', 'Trade'], item: str, description: str, price: int, currency: Literal['HUF', 'USD', 'EUR', 'GBP']):
    """Interact with the shop"""

    if action == 'Sell':
        logger.info(f"List order created: {item}")

        embed = discord.Embed(title='Marketplace - List Order')
        embed.description = f'```{description}```'
        embed.add_field(name='Seller', value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(name='Item', value=item, inline=True)
        embed.add_field(name='Action', value=action, inline=True)
        embed.add_field(name='Price', value=f'{price}{currency}', inline=True)

        sent = await interaction.response.send_message(embed=embed, ephemeral=True)

        await client.addMarketplaceItem(item, description, interaction.user.id, action, price, currency, 0),

    if action == 'Buy':
        logger.info(f"Buy order created: {item}")

        embed = discord.Embed(title='Marketplace - Buy Order')
        embed.description = f'```{description}```'
        embed.add_field(name='Buyer', value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(name='Item', value=item, inline=True)
        embed.add_field(name='Action', value=action, inline=True)
        embed.add_field(name='Price', value=f'{price}{currency}', inline=True)

        sent = await interaction.response.send_message(embed=embed, ephemeral=True)
        await client.addMarketplaceItem(item, description, interaction.user.id, action, price, currency, 0),

    if action == 'Trade':
        logger.info(f"Trade order created: {item}")

        embed = discord.Embed(title='Marketplace - Trade Order')
        embed.description = f'```{description}```'
        embed.add_field(name='Trader', value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(name='Item', value=item, inline=True)
        embed.add_field(name='Action', value=action, inline=True)
        embed.add_field(name='Price', value=f'{price}{currency}', inline=True)

        sent = await interaction.response.send_message(embed=embed, ephemeral=True)
        await client.addMarketplaceItem(item, description, interaction.user.id, action, price, currency, 0),

    channel = client.get_channel(config('SHOP_CHANNEL', cast=int))

    await channel.send(embed=embed)


@client.tree.command(name='delete', description='Deletes a marketplace item')
@app_commands.describe(item_id='The item id to delete')
async def delete(interaction: discord.Interaction, item_id: int):
    """Deletes a marketplace item"""

    await client.deleteMarketplaceItem(item_id, interaction.user.id)

    embed = discord.Embed(title='Marketplace - Deleted Item')
    embed.description = '```Item successfully deleted```'

    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name='update', description='Updates a marketplace item')
@app_commands.describe(item_id='The item id to update', action='The action to do in the shop', item='The target item')
async def update(interaction: discord.Interaction, item_id: int, action: Literal['Buy', 'Sell', 'Trade'], item: str, description: str, price: int, currency: Literal['HUF', 'USD', 'EUR', 'GBP']):
    """Updates a marketplace item"""

    if action == 'Sell':
        logger.info(f"List order updated: {item}")

        embed = discord.Embed(title='Marketplace - List Order')
        embed.description = f'```{description}```'
        embed.add_field(name='Seller', value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(name='Item', value=item, inline=True)
        embed.add_field(name='Action', value=action, inline=True)
        embed.add_field(name='Price', value=f'{price}{currency}', inline=True)

        await client.updateMarketplaceItem(item_id, item, description, interaction.user.id, action, price, currency, 0)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    if action == 'Buy':
        logger.info(f"Buy order updated: {item}")

        embed = discord.Embed(title='Marketplace - Buy Order')
        embed.description = f'```{description}```'
        embed.add_field(name='Buyer', value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(name='Item', value=item, inline=True)
        embed.add_field(name='Action', value=action, inline=True)
        embed.add_field(name='Price', value=f'{price}{currency}', inline=True)

        await client.updateMarketplaceItem(item_id, item, description, interaction.user.id, action, price, currency, 0)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    if action == 'Trade':
        logger.info(f"Trade order updated: {item}")

        embed = discord.Embed(title='Marketplace - Trade Order')
        embed.description = f'```{description}```'
        embed.add_field(name='Trader', value=f"<@{interaction.user.id}>", inline=False)
        embed.add_field(name='Item', value=item, inline=True)
        embed.add_field(name='Action', value=action, inline=True)
        embed.add_field(name='Price', value=f'{price}{currency}', inline=True)

        await client.updateMarketplaceItem(item_id, item, description, interaction.user.id, action, price, currency, 0)

        await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name='ping', description='Latency of the bot.')
@app_commands.describe()
async def ping(interaction: discord.Interaction):
    """Pong!"""

    # discord api ping
    api_ping = round(client.latency * 1000)

    # websocket ping
    ws_ping = round(client.ws.latency * 1000)

    embed = discord.Embed(title='Runner Latency')
    embed.description = '```Discord API & Websocket latency```'
    embed.add_field(name='API', value=f'```{api_ping}ms```', inline=True)
    embed.add_field(name='Websocket', value=f'```{ws_ping}ms```', inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name='help', description='Shows the list of available commands.')
@app_commands.describe()
async def help_command(interaction: discord.Interaction):
    """Shows the list of available commands."""

    embed = discord.Embed(title='Available Commands')
    for command in client.tree.walk_commands():
        embed.add_field(name=f'`/{command.name}`', value=command.description, inline=False)
    embed.set_footer(text='Use /<command> to get more info about a command.')

    await interaction.response.send_message(embed=embed, ephemeral=True)


client.run(BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)
