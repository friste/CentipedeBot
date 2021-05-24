import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import random

load_dotenv()
with open('token.txt') as f:
    TOKEN = f.readline()

PREFIX = '.'
DATA = 'data.json'

CENTIPEDES = {
    1: 'Common',
    2: 'Silver',
    3: 'Giratina',
    4: 'Black',
    5: 'Red'
}
PROFILE = 'centipede'
SLEEP = 'terrarium_sleep'
AWAKE = 'terrarium_awake'

MORNING = 6
NIGHT = 22

client = commands.Bot(command_prefix=PREFIX)


class Centipede:
    def __init__(self, owner: str, name: str, species: int):
        self.owner = owner
        self.name = name
        self.species = species
        self.health = 10
        self.energy = 10

    def catch(self):
        """
        adds entry initializing centipede to data.json
        """
        add(self.owner, {'name': self.name, 'species': self.species})


def read() -> dict:
    with open(DATA, "r") as f:
        return json.load(f)


def add(key: str, d: dict) -> None:
    """
    ADD NEW CENTIPEDE ENTRY TO data.json
    """
    with open(DATA, "r") as f:
        temp_dict = json.load(f)
        temp_dict[key] = d
    with open(DATA, "w") as f:
        json.dump(temp_dict, f, indent=2)


def delete(key: str) -> None:
    """
    DELETES CENTIPEDE ENTRY FROM data.json
    """
    with open(DATA, "r") as f:
        temp_dict = json.load(f)
        temp_dict.pop(key)
    with open(DATA, "w") as f:
        json.dump(temp_dict, f, indent=2)


def owns_centipede(owner: str) -> bool:
    with open(DATA, "r") as f:
        return True if owner in json.load(f) else False


def get_picture(prefix: str, index: int, extension: str):
    filename = prefix + str(index) + extension
    with open(filename, 'rb') as f:
        picture = discord.File(f)
    return picture


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=".help"))
    print(f'{client.user} has connected to Discord!')


@client.command()
async def catch(ctx):
    if owns_centipede(str(ctx.author)):
        await ctx.send('You already own a centipede! Try releasing it first.')
        return
    species = random.randint(1, 5)
    await ctx.send('You caught a ' + CENTIPEDES[species] + ' centipede!')
    await ctx.send(file=get_picture(PROFILE, species, '.png'))
    await ctx.send('Enter a name:')

    def check(message: discord.Message):
        return message.channel == ctx.channel and message.author != ctx.me and message.author == ctx.author

    name = await client.wait_for('message', check=check)

    c = Centipede(str(name.author), name.content, species)
    c.catch()
    await ctx.send('Congratulations! ' + name.content + ' is your new centipede!')


@client.command()
async def release(ctx):
    if not owns_centipede(str(ctx.author)):
        await ctx.send('You do not currently own a centipede.')
        return

    delete(str(ctx.author))
    await ctx.send('You released your centipede.')


@client.command()
async def rename(ctx):
    if not owns_centipede(str(ctx.author)):
        await ctx.send('You do not currently own a centipede.')
        return
    await ctx.send('Type a new name:')

    def check(message: discord.Message):
        return message.channel == ctx.channel and message.author != ctx.me and message.author == ctx.author

    name = await client.wait_for('message', check=check)
    entry = read()[str(ctx.author)]
    add(str(ctx.author), {'name': name.content, 'species': entry['species']})
    await ctx.send('You successfully renamed your centipede to ' + name.content + '.')


@client.command()
async def view(ctx):
    if not owns_centipede(str(ctx.author)):
        await ctx.send('You do not currently own a centipede.')
        return
    entry = read()[str(ctx.author)]
    await ctx.send("**" + entry['name'] + "**")
    hour = int(str(ctx.message.created_at).split()[-1][:2])
    await ctx.send(entry['name'] + ' is currently sleeping. Check back at night when they\'re active.')
    await ctx.send(file=get_picture(SLEEP, read()[str(ctx.author)]['species'], '.gif'))


@client.command()
async def fight(ctx, enemy: discord.Member):
    if not owns_centipede(str(ctx.author)):
        await ctx.send('You do not currently own a centipede.')
        return
    if not owns_centipede(str(enemy)):
        await ctx.send('Your opponent does not currently own a centipede.')
        return
    turn = 0
    hp1 = 100
    hp2 = 100
    c1 = read()[str(ctx.author)]['species']
    c2 = read()[str(enemy)]['species']

    moves = {'bite', 'heal', 'tail whip', 'flee'}
    enemy = enemy.mention
    me = ctx.message.author.mention
    if enemy == me:
        await ctx.send("Sadly, you can't fight yourself.")
        return
    while hp1 > 0 and hp2 > 0:
        # too much repetition, needs to be refactored
        if turn % 2 == 0:
            await ctx.send(f"{me} Select your move: `bite, heal, tail whip, or flee`")
            await ctx.send(file=get_picture(PROFILE, c1, '.png'))

            def check(m):
                return m.content in moves and m.author == ctx.message.author

            response = await client.wait_for('message', check=check)

            if "bite" in response.content.lower():
                await ctx.send("bite")
            elif "heal" in response.content.lower():
                await ctx.send("a nice test")
            elif "tail whip" in response.content.lower():
                await ctx.send("Congrats, nothing happened.")
            elif "flee" in response.content.lower():
                await ctx.send("a nice test")
                return

        elif turn % 2 == 1:
            await ctx.send(f"{enemy} Select your move: `bite, heal, tail whip, or flee`")
            await ctx.send(file=get_picture(PROFILE, c2, '.png'))

            def check(e):
                return e.content in moves and e.author == discord.Member

            response = await client.wait_for('message', check=check)

            if "test" in response.content.lower():
                await ctx.send("the test is strong with this one")
        turn = turn + 1


@client.command()
async def kill(ctx):
    if not owns_centipede(str(ctx.author)):
        await ctx.send('You do not currently own a centipede.')
        return

    n = random.randint(1, 3)
    name = read()[str(ctx.author)]['name']
    s1 = 'What is wrong with you?'
    s2 = 'You will one day face the moral consequences of this.'
    s3 = name + ' loves you...'
    delete(str(ctx.author))
    if n == 1:
        await ctx.send(s1)
    elif n == 2:
        await ctx.send(s2)
    elif n == 3:
        await ctx.send(s3)


@client.command()
async def hug(ctx):
    if not owns_centipede(str(ctx.author)):
        await ctx.send('You cannot hug your centipede because you do not own one.')
        return
    n = random.randint(1, 6)
    name = read()[str(ctx.author)]['name']

    s1 = 'This is not a good idea.'
    s2 = '{0} did not enjoy that. In fact, {0} is just one '.format(name) \
         + 'species of centipede that is venomous and gives extremely painful bites.'.format(name)
    s3 = 'You tenderly lift {0} from the terrarium, allowing '.format(name) \
        + 'the dozens of tiny legs to take hold of your arm. Somehow, you hug {0}, '.format(name) \
        + 'an action made physically possible for plot convenience. Sadly, you learn ' \
        + 'that {0} is not very affectionate. At the same time, you also learn that '.format(name) \
        + 'centipedes are venomous.'
    s4 = 'Try again.'
    s5 = 'You manage a hug, but suffer what might be the most painful animal bite known to humanity, and spend '\
        + 'the next hour writhing in pain.'
    s6 = 'Are you sure?'

    if n == 1:
        await ctx.send(s1)
    elif n == 2:
        await ctx.send(s2)
    elif n == 3:
        await ctx.send(s3)
    elif n == 4:
        await ctx.send(s4)
    elif n == 5:
        await ctx.send(s5)
    elif n == 6:
        await ctx.send(s6)

        def check(message: discord.Message):
            return message.channel == ctx.channel and message.author != ctx.me and message.author == ctx.author

        answer_temp = await client.wait_for('message', check=check)
        answer = answer_temp.content.strip().lower()
        if answer in {'yes', 'y', 'ye', 'yea', 'yeah'}:
            await ctx.send('This storyline is unavailable.')
        elif answer in {'no', 'n', 'nah'}:
            await ctx.send('Good choice.')


@client.command()
async def fact(ctx):
    lines = open('centipede_facts.txt').read().splitlines()
    await ctx.send(random.choice(lines))

client.run(TOKEN)
