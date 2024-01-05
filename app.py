import discord, dotenv, asyncio, os, io, cairosvg
from discord.ext import commands
from requests import get

dotenv.load_dotenv()
token = os.environ['TOKEN']

CHANNEL_ID = '1191097500136910858'

description = '''The official plot_bot for auto-trading, checks the plots of algorithms with diffirent intervals (daily, hourly, .......... )'''
algorithms = ['bollinger_bands', 'rsi', 'custom_bollinger_rsi', 'price']
plot_url = 'http://44.218.67.129:5000/plot'
intervals = [30, 60, 240, 1440]


async def plot(channel, plot_url):
    for algorithm in algorithms:
        files = []
        for interval in intervals:
            svg = get(plot_url + f'/{algorithm}?interval={interval}').content
            png_bytes = cairosvg.svg2png(bytestring=svg)
            png_file = io.BytesIO(png_bytes)
            files.append(
                discord.File(png_file, filename=f'{algorithm}{interval}.png'))

        await channel.send(
            content=
            f"Plotting algorithm : {algorithm}, at intervals : {intervals}",
            files=files)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

plot_bot = commands.Bot(command_prefix='/',
                        description=description,
                        intents=intents)


@plot_bot.event
async def on_ready():
    print(f'Logged in as {plot_bot.user} (ID: {plot_bot.user.id})')
    print('------')


@plot_bot.command(name='start_plotting')
async def start_loop(ctx):
    if ctx.channel.id == int(CHANNEL_ID):
        await ctx.send('Starting the loop in this channel...')
        channel = plot_bot.get_channel(int(CHANNEL_ID))

        while True:
            await plot(channel, plot_url)
            await asyncio.sleep(
                5 * 60 * 60
            )  #Adjust time , + dont make it speceficly work with intervals and update each time they update not necessary


plot_bot.run(token)
