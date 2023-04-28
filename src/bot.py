import random
import discord
import logging
import constants

from typing import Literal, Union
from discord import app_commands

from market import Market

BOT_TOKEN = constants.DC_BOT_TOKEN
MY_GUILD = constants.GUILD_ID

discord.utils.setup_logging()

logger = logging.getLogger(str(__name__).upper())

logging.getLogger("discord.client").setLevel(logging.WARN)
logging.getLogger("discord.gateway").setLevel(logging.WARN)


class MarketClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())

        self.tree = app_commands.CommandTree(self)
        self.market = Market()

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)

        await self.tree.sync(guild=MY_GUILD)


bot = MarketClient()


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logger.info('-' * 50)

@bot.event
async def on_ratelimit(rate_limit):
    logger.warning(f'Rate limited for {rate_limit} seconds')


@bot.tree.command(name='roll', description='Rolls the dice')
@app_commands.describe()
async def roll(interaction: discord.Interaction):
    """Rolls a dice"""

    roll_embed = discord.Embed(title='Rolling Dice')
    roll_embed.add_field(name='You rolled', value=f'```{random.randint(1, 6)}```', inline=True)

    await interaction.response.send_message(embed=roll_embed, ephemeral=True)


@bot.tree.command(name='channel-info', description='Shows basic channel info for a text or voice channel')
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

@bot.tree.command(name='server-info', description='Shows basic server info')
@app_commands.describe()
async def server_info(interaction: discord.Interaction):
    """Shows basic server info"""

    guild = interaction.guild

    embed = discord.Embed(title='Server Info')

    embed.add_field(name='Name', value=guild.name, inline=False)
    embed.add_field(name='ID', value=guild.id, inline=False)
    embed.add_field(name='Owner', value=f'<@{guild.owner_id}>', inline=False)
    # embed.add_field(name='Categories', value=len(guild.categories), inline=True)
    embed.add_field(name='Members', value=guild.member_count, inline=True)
    embed.add_field(name='Channels', value=len(guild.channels), inline=True)
    embed.add_field(name='Roles', value=len(guild.roles), inline=True)

    embed.set_footer(text='Created').timestamp = guild.created_at

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name='marketplace', description='Shows the marketplace items')
@app_commands.describe()
async def marketplace(interaction: discord.Interaction, page: app_commands.Range[int, 1, None] = 1,
                      limit: app_commands.Range[int, 1, 10] = 10):
    """Shows the marketplace items"""

    items = await bot.market.paginate_items(page, limit)

    embed = discord.Embed(title='Marketplace - Available Listings')

    if len(items) == 0:
        embed.description = '```There are no items in the marketplace```'

    for item in items:
        embed.add_field(name=f"`{item.id}`",
                        value=f"{str(item.listing).lower().capitalize()} order for `{item.name}` by <@{item.actor}> for `{item.price}{item.currency}`",
                        inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='shop', description='Interact with the shop')
@app_commands.describe(action='The action to do in the shop', item='The target item')
async def shop(interaction: discord.Interaction, action: Literal['Buy', 'Sell', 'Trade'], item: str, description: str,
               price: int, currency: Literal['HUF', 'USD', 'EUR', 'GBP']):
    """Interact with the shop"""

    embed = discord.Embed(title=f'{item} - List Order')
    embed.description = f'```{description}```'
    embed.add_field(name='Seller', value=f"<@{interaction.user.id}>", inline=True)
    embed.add_field(name='Action', value=action, inline=True)
    embed.add_field(name='Price', value=f'{price}{currency}', inline=True)

    SHOP_CHANNEL = bot.get_channel(constants.SHOP_CHANNEL)

    sent = await SHOP_CHANNEL.send(embed=embed)

    await bot.market.add_item(item, description, interaction.user.id, action, price, currency, sent.id)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='delete', description='Deletes a marketplace item')
@app_commands.describe(item_id='The item id to delete')
async def delete(interaction: discord.Interaction, item_id: int):
    """Deletes a marketplace item"""

    item = await bot.market.get_item(item_id)
    await bot.market.delete_item(item_id, interaction.user.id)

    embed = discord.Embed(title='Marketplace - Deleted Item')
    embed.description = '```Item successfully deleted```'

    SHOP_CHANNEL = bot.get_channel(constants.SHOP_CHANNEL)

    try:
        message = await SHOP_CHANNEL.fetch_message(item.message_id)
        
        await message.delete()
    except discord.NotFound:
        logger.error(f'Could not find message with id {item.message_id}, probably already deleted/sold')
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='update', description='Updates a marketplace item')
@app_commands.describe(item_id='The item id to update', action='The action to do in the shop', item='The target item')
async def update(interaction: discord.Interaction, item_id: int, action: Literal['Buy', 'Sell', 'Trade'], item: str,
                 status: Literal['Available', 'Sold', 'Pending'],
                 description: str, price: int, currency: Literal['HUF', 'USD', 'EUR', 'GBP']):
    """Updates a marketplace item"""

    embed = discord.Embed(title=f'{item} - {action} Order')
    embed.description = f'```{description}```'
    embed.add_field(name='Seller', value=f"<@{interaction.user.id}>", inline=True)
    embed.add_field(name='Action', value=action, inline=True)
    embed.add_field(name='Price', value=f'{price}{currency}', inline=True)

    await bot.market.update_item(item_id, item, status, description, interaction.user.id, action, price, currency)
    await interaction.response.send_message(embed=embed, ephemeral=True)

    SHOP_CHANNEL = bot.get_channel(constants.SHOP_CHANNEL)

    fetched_item = await bot.market.get_item(item_id)
    message = await SHOP_CHANNEL.fetch_message(fetched_item.message_id)

    await message.edit(embed=embed)

    if status == 'Sold' or status == 'Pending':
        await message.delete()


@bot.tree.command(name='ping', description='Latency of the bot.')
@app_commands.describe()
async def ping(interaction: discord.Interaction):
    """Pong!"""

    api_ping = round(bot.latency * 1000)
    ws_ping = round(bot.ws.latency * 1000)

    embed = discord.Embed(title='Runner Latency')
    embed.description = '```Discord API & Websocket latency```'
    embed.add_field(name='API', value=f'```{api_ping}ms```', inline=True)
    embed.add_field(name='Websocket', value=f'```{ws_ping}ms```', inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='help', description='Shows the list of available commands.')
@app_commands.describe()
async def help_command(interaction: discord.Interaction):
    """Shows the list of available commands."""

    embed = discord.Embed(title='Available Commands')

    for command in bot.tree.walk_commands():
        embed.add_field(name=f'`/{command.name}`', value=command.description, inline=False)

    embed.set_footer(text='Use /<command> to get more info about a command.')

    await interaction.response.send_message(embed=embed, ephemeral=True)


def start():
    bot.run(BOT_TOKEN)
