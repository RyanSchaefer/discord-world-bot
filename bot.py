'''
'''
import asyncio
import os
import pickle
import random
import datetime

from discord.ext import commands

import btoken
import world_config

import logging
# create logger with 'spam_application'
logger = logging.getLogger('world_bot')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
if not os.path.isdir('logs'):
    os.mkdir('logs')
fh = logging.FileHandler(os.path.join('logs', '{}.log'.format(datetime.datetime.today().isoformat(' ').replace(':', ';'))))
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

bot = commands.Bot(command_prefix="!", description="Simulating a progressing world.\
 Currently World development is in {}. Here's a helpful tip: {}".format(\
 world_config.era, random.choice(world_config.tips)))
if not os.path.isdir('users'):
    os.mkdir('users')
class Player(object):
    '''
    One user of the discord bot.
    '''
    def __init__(self):
        self.inventory = {}
        self.coords = {'x': random.randint(0, 1000), 'y': random.randint(0, 1000)}
        self.status = ''
        self.speed = 0
    def initialize_item(self, item):
        '''
        Add a new item to the users inv based and limit it based on the config file
        '''
        self.inventory.update({item:{'amount':0, 'item_info': world_config.items[item]}})
    def add_item(self, item, amount):
        '''
        Add an amount of item, can be a negative number to take away
        '''
        try:
            item = self.inventory[item]
            new_total = item['amount'] + amount
            limit = item['item_info']['limit']
            if new_total <= limit and new_total >= 0:
                item['amount'] = new_total
                return True
            elif new_total > limit:
                item['amount'] = limit
                return 'LimitReached'
            elif new_total < 0:
                return 'LessThanZero'
        except KeyError:
            self.initialize_item(item)
            item = self.inventory[item]
            new_total = item['amount'] + amount
            limit = item['item_info']['limit']
            if new_total <= limit and new_total >= 0:
                item['amount'] = new_total
                return True
            elif new_total > limit:
                item['amount'] = limit
                return False
            elif new_total < 0:
                return False


logger.info('Loading map.')


if not os.path.isdir('resources'):
    os.mkdir('resources')
    open(os.path.join('resources', 'map'), 'w').write('')
    WORLD = {}
elif os.path.isfile(os.path.join('resources', 'map')):
    open(os.path.join('resources', 'map'), 'w').write('')
    WORLD = {}
else:
    WORLD = pickle.load(open(os.path.join('resources', 'map'), 'rb'))
if WORLD == {}:
    for x in range(1000):
        WORLD.update({x:{}})
        for y in range(1000):
            WORLD[x].update({y:{}})

logger.info('Loading world_config into users.')

for user in os.listdir('users'):
    luser = pickle.load(open(os.path.join('users', user), 'rb'))
    luser.status = ''
    for item in list(world_config.items):
        try:
            if item in list(luser.inventory):
                amount = luser.inventory[item]['amount']
                del luser.inventory[item]
                luser.add_item(item, amount)
        except KeyError:
            pass
    luser.status = ''
    for item in list(luser.inventory):
        if item not in list(world_config.items):
            del luser.inventory[item]
    pickle.dump(luser, open(os.path.join('users', user), 'wb'))

def create_player(ctx):
    member = ctx.message.author
    if member.id not in os.listdir('users') and not member.bot:
        pickle.dump(Player(), open(os.path.join('users', member.id), 'wb'))
        logger.info('Created new player with id of {}'.format(member.id))
    else:
        pass


def explicit_parse_record(userid):
    explicit_create_player(userid)
    return pickle.load(open(os.path.join('users', userid), 'rb'))


def explicit_create_player(userid):
    if userid not in os.listdir('users'):
        pickle.dump(Player(), open(os.path.join('users', userid), 'wb'))
        logger.info('Created new player with id of {}'.format(member.id))
    else:
        pass
def explicit_save_record(userid, player_obj): 
    pickle.dump(player_obj, open(os.path.join('users', userid), 'wb'))


def parse_record(ctx):
    create_player(ctx)
    return pickle.load(open(os.path.join('users', ctx.message.author.id), 'rb'))


def save_record(ctx, player_obj):
    pickle.dump(player_obj, open(os.path.join('users', ctx.message.author.id), 'wb'))


@bot.event
async def on_ready():
    print("Bot Joined Channel")
    logger.info('Bot started.')
    while True:
        print('autosaving map')
        pickle.dump(WORLD, open(os.path.join('resources', 'map'), 'wb'))
        await asyncio.sleep(60)

@bot.group(pass_context=True)
async def admin(ctx):
    pass

@admin.command(pass_context=True)
async def edit(ctx, player_id: str, attr: str, value_change: int):
    '''
    Edit a users stat. Uses player.__dict__[stat] for editing
    '''
    user = ctx.message.author.id
    if user in world_config.admins:
        try:
            target = explicit_parse_record(player_id)
            old_value = target.__dict__[attr]
            target.__dict__[attr] = value_change
            explicit_save_record(player_id, target)
            await bot.say('Edited {} for {} to {}'.format(attr, player_id, value_change))
            logger.critical('{} changed {} for {} from {} to {}'.format(user, attr, player_id, old_value, value_change))
        except KeyError:
            bot.say('Could not edit {}'.format(attr))
    else:
        await bot.say(random.choice(world_config.admin_failed))


@admin.command(pass_context=True)
async def add(ctx, player_id: str, item: str, amount: int):
    '''
    Adds an amount of item to a player.
    '''
    user = ctx.message.author.id
    if user in world_config.admins:
        try:
            target = explicit_parse_record(player_id)
            target.add_item(item, amount)
            explicit_save_record(player_id, target)
            await bot.say('Added {} {} to {}'.format(item, player_id, amount))
            logger.critical('{} added {} {} to {}'.format(user, amount, item, player_id))
        except KeyError:
            await bot.say('Could not set {}'.format(item))
    else:
        await bot.say(random.choice(world_config.admin_failed))


@admin.command(pass_context=True)
async def myid(ctx):
    '''
    Displays an admins ID. Used to get ID for testing purposes
    '''
    if ctx.message.author.id in world_config.admins:
        await bot.say('Your id is: {}'.format(ctx.message.author.id))
        logger.info('{} looked up their id.'.format(ctx.message.author.id))


@bot.command(pass_context=True)
async def coords(ctx):
    '''
    Displays the users current coordinates.
    '''
    user = parse_record(ctx)
    await bot.say('`Current coords: {x}, {y}`'.format(**user.coords))


@bot.command(pass_context = True)
async def produce(ctx, product: str, runs: int = 1, tool: str = None):
    '''
    Used to produce any product. Producing basic products does not require any substrates. Producing more complex items requires other items as substrates.
    '''
    user = parse_record(ctx)
    if product in list(world_config.items):
        if tool is None:
            toolbonus = 0
            timereduction = 0
        else:
            try:
                toolbonus = user.inventory[tool]['item_info']['toolbonus']
                if product in toolbonus:
                    toolbonus = toolbonus[product]
                else:
                    toolbonus = 0
            except KeyError:
                toolbonus = 0
            try:
                timereduction = user.inventory[tool]['item_info']['toolbonus']
                if product in timereduction:
                    timereduction = timereduction[product]
                else:
                    timereduction = 0
            except KeyError:
                timereduction = 0
            if timereduction == 0 and toolbonus == 0:
                await bot.say('Could not use {} on {}. Type !inventory to see if you have a {}'.format(tool, product, tool))
        substrates = world_config.items[product]['substrates']
        if 'producing' not in user.status:
            user.status = 'producing {}'.format(product)
            save_record(ctx, user)
            for nullvariable in range(runs):
                cinv = user.inventory
                for substrate in substrates:
                    response = user.add_item(substrate, substrates[substrate])
                    if response == 'LessThanZero':
                        user.inventory = cinv
                        await bot.say('You do not have the substrates to produce {}'.format(\
                        product))
                        return False
                low, high = world_config.items[product]['product_range']
                amount = random.randint(low, high)
                amount += round(amount * toolbonus)
                waittime = world_config.items[product]['time_to_produce']
                waittime -= round(waittime * timereduction)
                if user.add_item(product, amount) != 'LimitReached':
                    if waittime >= 5:
                        await bot.say(\
                        '{} will take approximately {} seconds to per product to produce.'.format(\
                        product, waittime))
                        await asyncio.sleep(waittime)
                        await bot.say('You produce {} {}'.format(amount, product))
                    else:
                        await asyncio.sleep(waittime)
                        await bot.say('You produce {} {}'.format(amount, product))
                else:
                    await bot.say(\
                    'You have reached the maximum amount of {} you can carry.'.format(\
                    product))
                    user.inventory = cinv
                    break
        user.status = ''
        save_record(ctx, user)
    else:
        await bot.say('{} is cannot be produced.'.format(product))


@bot.command(pass_context = True)
async def inv(ctx, item: str):
    '''
    Returns the amount of an item you have in your inventory.
    '''
    user = parse_record(ctx)
    if item in list(user.inventory):
        await bot.say('You have {} {} in your inventory'.format(\
        item, user.inventory[item]['amount']))
    else:
        await bot.say('You do not currently have {} in your inventory'.format(item))


@bot.command(pass_context = True)
async def move(ctx, x_coord: int, y_coord: int):
    '''
    Moves the player to a coordinate. If the user has a vehicle it will be significantly faster.
    '''
    if (x_coord >= 0 and y_coord >= 0) and (x_coord <= 999 and y_coord <= 999):
        user = parse_record(ctx)
        distance = abs(user.coords['x'] - x_coord) + abs(user.coords['y'] - y_coord)
        waittime = distance * 60 - round(user.speed * distance)
        await bot.say('It will take approximately {}s to move {}u. Are you sure you want to travel y/n?'.format(waittime, distance))
        msg = await bot.wait_for_message(timeout=10, author=ctx.message.author)
        if msg.content == 'y' and 'traveling' != user.status:
            await bot.say('Traveling...')
            user.status = 'traveling'
            save_record(ctx, user)
            for x in range(abs(user.coords['x'] - x_coord)):
                if user.coords['x'] < x_coord:
                    user.coords['x'] += 1
                    await asyncio.sleep(60 - round(user.speed))
                elif user.coords['x'] > x_coord:
                    user.coords['x'] -= 1
                    await asyncio.sleep(60 - round(user.speed))
            for x in range(abs(user.coords['y'] - y_coord)):
                if user.coords['y'] < y_coord:
                    user.coords['y'] += 1
                    await asyncio.sleep(60 - round(user.speed))
                elif user.coords['y'] > y_coord:
                    user.coords['y'] -= 1
                    await asyncio.sleep(60 - round(user.speed))
            await bot.say('You have reached {} {}'.format(x_coord, y_coord))
            user.status = ''
            save_record(ctx, user)
        elif 'traveling' == user.status:
            await bot.say('You are currently traveling.')

@bot.command(pass_context=True)
async def item(ctx, item):
    if item in world_config.items:
        name = item
        item = world_config.items[item]
        substrate_list = []
        for x in item['substrates']:
            substrate_list.append('{} : {}'.format(x, item['substrates'][x]*-1))
        if {} == item['substrates']:
            substrate_list = ['none']
        await bot.say(
'''{} information:
Substrates:\n`{}`
Time to produce: `{}`
Product range: `{}`
'''.format(name, '\n'.join(substrate_list), item['time_to_produce'], item['product_range'])
        )


@bot.event
async def on_member_join(member):
    if member.id not in os.listdir('users') and not member.bot:
        open(os.path.join('users', member.id), 'w').write("")


bot.run(btoken.token)
