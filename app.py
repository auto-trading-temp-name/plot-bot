import dotenv, os, io, schedule
from discord import Intents, File, app_commands
from threading import Thread
from discord.ext import commands
from cairosvg import svg2png
from requests import get
from time import sleep

dotenv.load_dotenv()

description = '''The official Discord plotting bot for auto-trading.
Checks plots of a few algorithms at different intervals
to check market conditions, check for buy and sell signals, or anything else
'''
algorithms = ['bollinger_bands', 'rsi', 'custom_bollinger_rsi', 'price']
intervals = [30, 60, 240, 1440]
channel_id = int(os.environ['CHANNEL_ID'])
channel = None

async def plot():
	if channel is None:
		return

	for algorithm in algorithms:
		files = []
		for interval in intervals:
			svg = get(f'{os.environ["BASE_URL"]}/{algorithm}?interval={interval}').content
			png_bytes = svg2png(bytestring=svg)
			png_file = io.BytesIO(png_bytes)
			files.append(File(png_file, filename=f'{algorithm}{interval}.png'))

		interval_copy = [*intervals]
		interval_copy[-1] = f'and {interval_copy[-1]}'
		await channel.send(content=f"Plotting algorithm {algorithm} at intervals {', '.join(interval_copy)}", files=files)

def job_loop():
	while True:
		schedule.run_pending()
		sleep(1)

bot = commands.Bot(command_prefix='/', description=description, intents=Intents.default())
thread = Thread(target=job_loop, daemon=True)

@bot.event
async def on_ready():
	print(f'Logged in as {bot.user} (ID: {bot.user.id})')
	schedule.every(intervals[0] + 14).minutes.do(plot)

	try:
		synced = await bot.tree.sync()
		print(f'Synced {len(synced)} commands')
	except Exception:
		pass

@bot.tree.command(name='start_plotting')
@app_commands.check(lambda interaction: interaction.channel.id == channel_id)
@app_commands.default_permissions(manage_guild=True)
async def start_loop(interaction):
	global channel
	await interaction.response.send_message('Starting loop...', silent=True)

	channel = interaction.channel
	schedule.run_all()
	thread.start()

bot.run(os.environ['TOKEN'])
