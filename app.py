import dotenv, os, io, asyncio, schedule
from discord import Intents, File, app_commands
from discord.ext import commands
from datetime import datetime, timedelta
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
continue_running = True
next_run = datetime.now()

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

		message = await channel.send(content=f"Plotting algorithm {algorithm} at intervals {intervals}", files=files)
		await message.publish()

bot = commands.Bot(command_prefix='/', description=description, intents=Intents.default())

def get_next_run(time_format='human'):
	seconds = (next_run - datetime.now()).total_seconds()
	return seconds / 60.0 if time_format == 'minutes' else seconds if time_format == 'seconds' else f'{int(seconds // 60)}:{int(seconds % 60)}'

@bot.event
async def on_ready():
	global continue_running, next_run
	print(f'Logged in as {bot.user} (ID: {bot.user.id})')

	try:
		synced = await bot.tree.sync()
		print(f'Synced {len(synced)} commands')

		while True:
			if continue_running:
				await plot()
			next_run = datetime.now() + timedelta(minutes=15)
			await asyncio.sleep(15 * 60)
	except Exception:
		pass

@bot.tree.command(name='start_plotting')
@app_commands.check(lambda interaction: interaction.channel.id == channel_id)
@app_commands.default_permissions(manage_guild=True)
async def start_loop(interaction):
	global channel, continue_running, thread
	await interaction.response.send_message(f'Starting plots. Next run is in {get_next_run()}', ephemeral=True)

	channel = interaction.channel
	continue_running = True

@bot.tree.command(name='stop_plotting')
@app_commands.default_permissions(manage_guild=True)
async def stop_loop(interaction):
	global continue_running
	await interaction.response.send_message('Stopping plots', ephemeral=True)
	continue_running = False

@bot.tree.command(name='force_plot')
@app_commands.default_permissions(manage_guild=True)
async def force_plot(interaction):
	global continue_running
	await interaction.response.send_message('Sending plots instantly', ephemeral=True)
	await plot()

@bot.tree.command(name='status')
async def status(interaction):
	global continue_running
	await interaction.response.send_message(
	  f'Plotting is currently {"enabled" if continue_running else "disabled"}\nNext plot is in {get_next_run()}')

bot.run(os.environ['TOKEN'])
