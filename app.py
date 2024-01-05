import discord, dotenv, asyncio, os, io, cairosvg
from discord.ext import commands
from requests import get

dotenv.load_dotenv()

description = '''The official plot_bot for auto-trading, checks the plots of algorithms with diffirent intervals (daily, hourly, .......... )'''
algorithms = ['bollinger_bands', 'rsi', 'custom_bollinger_rsi', 'price']
intervals = [30, 60, 240, 1440]
channel_id = os.environ['CHANNEL_ID']

async def plot(channel):
	for algorithm in algorithms:
		files = []
		for interval in intervals:
			svg = get(os.environ['BASE_URL'] + f'/{algorithm}?interval={interval}').content
			png_bytes = cairosvg.svg2png(bytestring=svg)
			png_file = io.BytesIO(png_bytes)
			files.append(discord.File(png_file, filename=f'{algorithm}{interval}.png'))

		await channel.send(content=f"Plotting algorithm : {algorithm}, at intervals : {intervals}", files=files)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

plot_bot = commands.Bot(command_prefix='/', description=description, intents=intents)

@plot_bot.event
async def on_ready():
	print(f'Logged in as {plot_bot.user} (ID: {plot_bot.user.id})')
	print('------')

@plot_bot.command(name='start_plotting')
async def start_loop(ctx):
	if ctx.channel.id == channel_id:
		await ctx.send('Starting the loop in this channel...')
		channel = plot_bot.get_channel(channel_id)

		while True:
			await plot(channel)
			await asyncio.sleep(
			  intervals[0] * 60 * 60
			)  #Adjust time , + dont make it speceficly work with intervals and update each time they update not necessary

plot_bot.run(os.environ['TOKEN'])
