import discord

from decouple import config
from dotenv import load_dotenv

load_dotenv()

DC_BOT_TOKEN = str(config('DC_BOT_TOKEN'))
GUILD_ID = discord.Object(id=config('GUILD_ID', cast=int))
SHOP_CHANNEL = config('SHOP_CHANNEL', cast=int)
