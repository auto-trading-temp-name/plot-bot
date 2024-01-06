import dotenv, os, io, asyncio, schedule
from discord import Intents, File, app_commands
from discord.ext import commands
from datetime import datetime
from cairosvg import svg2png
from requests import get

dotenv.load_dotenv()

description = '''The official Discord plotting bot for auto-trading.
Checks plots of a few algorithms at different intervals
to check market conditions, check for buy and sell signals, or anything else
'''
algorithms = ['bollinger_bands', 'rsi', 'custom_bollinger_rsi', 'price']
intervals = [30, 60, 240, 1440]
channel_id = int(os.environ['CHANNEL_ID'])
channel = None
run_plots = False
continue_running = True

async def plot():
	global algorithms, intervals
	if channel is None:
		return

	for algorithm in algorithms:
		files = []
		for interval in intervals:
			svg = get(f'{os.environ["BASE_URL"]}/{algorithm}?interval={interval}').content
			png_bytes = svg2png(bytestring=svg)
			png_file = io.BytesIO(png_bytes)
			files.append(File(png_file, filename=f'{algorithm}{interval}.png'))

		await channel.send(content=f"Plotting algorithm {algorithm} at intervals {intervals}", files=files)

bot = commands.Bot(command_prefix='/', description=description, intents=Intents.default())

def job_function():
	global run_plots
	run_plots = True

def get_next_run(time_format='human'):
	seconds = ((schedule.jobs[0].next_run or datetime.now()) - datetime.now()).total_seconds()
	return seconds / 60.0 if time_format == 'minutes' else seconds if time_format == 'seconds' else f'{int(seconds // 60)}:{int(seconds % 60)}'

@bot.event
async def on_ready():
	global run_plots, continue_running
	print(f'Logged in as {bot.user} (ID: {bot.user.id})')
	schedule.every().hour.at(f':{intervals[0]}').do(job_function)

	try:
		synced = await bot.tree.sync()
		print(f'Synced {len(synced)} commands')

		while True:
			if continue_running:
				schedule.run_pending()
				if run_plots:
					run_plots = False
					await plot()
			await asyncio.sleep(1)
	except Exception:
		pass

@bot.tree.command(name='start_plotting')
@app_commands.check(lambda interaction: interaction.channel.id == channel_id)
@app_commands.default_permissions(manage_guild=True)
async def start_loop(interaction):
	global channel, continue_running, thread
	await interaction.response.send_message(f'Starting plots. Next run is in {get_next_run()}', silent=True)

	channel = interaction.channel
	continue_running = True

@bot.tree.command(name='stop_plotting')
@app_commands.default_permissions(manage_guild=True)
async def stop_loop(interaction):
	global continue_running
	await interaction.response.send_message('Stopping plots', silent=True)
	continue_running = False

@bot.tree.command(name='status')
async def status(interaction):
	global continue_running
	await interaction.response.send_message(
	  f'Plotting is currently {"enabled" if continue_running else "disabled"}\nNext plot is in {get_next_run()}')

bot.run(os.environ['TOKEN'])
