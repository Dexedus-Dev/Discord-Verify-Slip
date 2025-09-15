from func.image import *
from func.sendSlip import *
from func.discord import *
import os
from dotenv import load_dotenv

load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))
