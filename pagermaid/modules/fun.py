""" Fun related chat utilities. """

from asyncio import sleep
from random import choice, random, randint, randrange, seed
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from cowpy import cow
from pagermaid import module_dir
from pagermaid.listener import listener
from pagermaid.utils import owoify, execute, random_gen, obtain_message, lang


@listener(is_plugin=False, outgoing=True, command="animate",
          description=lang('animate_des'),
          parameters="<message>")
async def animate(context):
    """ Make a text animation using a message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    interval = 0.3
    words = message.split(" ")
    count = 0
    buffer = ""
    while count != len(words):
        await sleep(interval)
        buffer = f"{buffer} {words[count]}"
        await context.edit(buffer)
        count += 1


@listener(is_plugin=False, outgoing=True, command="teletype",
          description=lang('teletype_des'),
          parameters="<message>")
async def teletype(context):
    """ Makes a typing animation via edits to the message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    interval = 0.03
    cursor = "█"
    buffer = ''
    await context.edit(cursor)
    await sleep(interval)
    for character in message:
        buffer = f"{buffer}{character}"
        buffer_commit = f"{buffer}{cursor}"
        await context.edit(buffer_commit)
        await sleep(interval)
        try:
            await context.edit(buffer)
        except MessageNotModifiedError:
            pass
        await sleep(interval)


@listener(is_plugin=False, outgoing=True, command="mock",
          description=lang('mock_des'),
          parameters="<message>")
async def mock(context):
    """ Mock people with weird capitalization. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    result = mocker(message)
    reply = await context.get_reply_message()
    await context.edit(result)
    if reply:
        if reply.sender.is_self:
            try:
                await reply.edit(result)
            except MessageNotModifiedError:
                await context.edit("A rare event of two mocking messages being the same just occurred.")
                return
            await context.delete()


@listener(is_plugin=False, outgoing=True, command="widen",
          description=lang('widen_des'),
          parameters="<message>")
async def widen(context):
    """ Widens every character in a string. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    wide_map = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))
    wide_map[0x20] = 0x3000
    result = str(message).translate(wide_map)
    reply = await context.get_reply_message()
    await context.edit(result)
    if reply:
        if reply.sender.is_self:
            try:
                await reply.edit(result)
            except MessageNotModifiedError:
                await context.edit(lang('widen_already'))
                return
            await context.delete()


@listener(is_plugin=False, outgoing=True, command="fox",
          description=lang('fox_des'),
          parameters="<message>")
async def fox(context):
    """ Makes a fox scratch your message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    result = corrupt(" ".join(message).lower())
    await edit_reply(result, context)


@listener(is_plugin=False, outgoing=True, command="owo",
          description=lang('owo_des'),
          parameters="<message>")
async def owo(context):
    """ Makes messages become OwO. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    result = owoify(message)
    await edit_reply(result, context)


@listener(is_plugin=False, outgoing=True, command="flip",
          description=lang('flip_des'),
          parameters="<message>")
async def flip(context):
    """ Flip flops the message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    result = message[::-1]
    await edit_reply(result, context)


@listener(is_plugin=False, outgoing=True, command="ship",
          description=lang('ship_des'),
          parameters="<username> <username>")
async def ship(context):
    """ Ship randomly generated members. """
    await context.edit(lang('ship_processing'))
    if len(context.parameter) == 0:
        users = []
        async for user in context.client.iter_participants(context.chat_id):
            users.append(user)
        target_1 = choice(users)
        target_2 = choice(users)
        if len(users) == 1:
            target_1 = users[0]
            target_2 = await context.client.get_me()
    elif len(context.parameter) == 1:
        users = []
        user_expression = int(context.parameter[0]) if context.parameter[0].isnumeric() else context.parameter[0]
        try:
            target_1 = await context.client.get_entity(user_expression)
        except BaseException:
            await context.edit(lang('ship_BaseException'))
            return
        async for user in context.client.iter_participants(context.chat_id):
            users.append(user)
        target_2 = choice(users)
    elif len(context.parameter) == 2:
        user_expression_1 = int(context.parameter[0]) if context.parameter[0].isnumeric() else context.parameter[0]
        user_expression_2 = int(context.parameter[1]) if context.parameter[1].isnumeric() else context.parameter[1]
        try:
            target_1 = await context.client.get_entity(user_expression_1)
            target_2 = await context.client.get_entity(user_expression_2)
        except BaseException:
            await context.edit(lang('ship_BaseException'))
            return
    else:
        await context.edit(lang('arg_error'))
        return
    await context.edit(f"**{lang('ship_hint')}（（（**\n"
                       f"[{target_1.first_name}](tg://user?id={target_1.id}) + "
                       f"[{target_2.first_name}](tg://user?id={target_2.id}) = ❤️")


@listener(is_plugin=False, outgoing=True, command="rng",
          description=lang('rng_des'),
          parameters="<length>")
async def rng(context):
    """ Generates a random string with a specific length. """
    if len(context.parameter) == 0:
        await context.edit(await random_gen("A-Za-z0-9"))
        return
    if len(context.parameter) == 1:
        try:
            await context.edit(await random_gen("A-Za-z0-9", int(context.parameter[0])))
        except ValueError:
            await context.edit(lang('arg_error'))
        return
    await context.edit(lang('arg_error'))


@listener(is_plugin=False, outgoing=True, command="aaa",
          description=lang('aaa_des'),
          parameters="<integer>")
async def aaa(context):
    """ Saves a few presses of the A and shift key. """
    if len(context.parameter) == 0:
        await context.edit(await random_gen("Aa"))
        return
    if len(context.parameter) == 1:
        try:
            await context.edit(await random_gen("Aa", int(context.parameter[0])))
        except ValueError:
            await context.edit(lang('arg_error'))
        return
    await context.edit(lang('arg_error'))


@listener(is_plugin=False, outgoing=True, command="asciiart",
          description=lang('asciiart_des'),
          parameters="<string>")
async def asciiart(context):
    """ Generates ASCII art of specified string. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    result = await execute(f"figlet -f {module_dir}/assets/graffiti.flf '{message}'")
    await context.edit(f"```\n{result}\n```")


@listener(is_plugin=False, outgoing=True, command="tuxsay",
          description=lang('tuxsay_des'),
          parameters="<message>")
async def tuxsay(context):
    """ Generates ASCII art of Tux saying a specific message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    result = cow.Tux().milk(message)
    await context.edit(f"```\n{result}\n```")


@listener(is_plugin=False, outgoing=True, command="coin",
          description=lang('coin_des'))
async def coin(context):
    """ Throws a coin. """
    await context.edit(lang('coin_processing'))
    await sleep(.5)
    outcomes = ['A'] * 5 + ['B'] * 5 + ['C'] * 1
    result = choice(outcomes)
    count = 0
    while count <= 3:
        await context.edit("`.` . .")
        await sleep(.3)
        await context.edit(". `.` .")
        await sleep(.3)
        await context.edit(". . `.`")
        await sleep(.3)
        count += 1
    if result == "C":
        await context.edit(lang('coin_lost'))
    elif result == "B":
        await context.edit("Tails!")
    elif result == "A":
        await context.edit("Heads!")


def mocker(text, diversity_bias=0.5, random_seed=None):
    """ Randomizes case in a string. """
    if diversity_bias < 0 or diversity_bias > 1:
        raise ValueError('diversity_bias must be between the inclusive range [0,1]')
    seed(random_seed)
    out = ''
    last_was_upper = True
    swap_chance = 0.5
    for c in text:
        if c.isalpha():
            if random() < swap_chance:
                last_was_upper = not last_was_upper
                swap_chance = 0.5
            c = c.upper() if last_was_upper else c.lower()
            swap_chance += (1 - swap_chance) * diversity_bias
        out += c
    return out


def corrupt(text):
    """ Summons fox to scratch strings. """
    num_accents_up = (1, 3)
    num_accents_down = (1, 3)
    num_accents_middle = (1, 2)
    max_accents_per_letter = 3
    dd = ['̖', ' ̗', ' ̘', ' ̙', ' ̜', ' ̝', ' ̞', ' ̟', ' ̠', ' ̤', ' ̥', ' ̦', ' ̩', ' ̪', ' ̫', ' ̬', ' ̭', ' ̮',
          ' ̯', ' ̰', ' ̱', ' ̲', ' ̳', ' ̹', ' ̺', ' ̻', ' ̼', ' ͅ', ' ͇', ' ͈', ' ͉', ' ͍', ' ͎', ' ͓', ' ͔', ' ͕',
          ' ͖', ' ͙', ' ͚', ' ', ]
    du = [' ̍', ' ̎', ' ̄', ' ̅', ' ̿', ' ̑', ' ̆', ' ̐', ' ͒', ' ͗', ' ͑', ' ̇', ' ̈', ' ̊', ' ͂', ' ̓', ' ̈́', ' ͊',
          ' ͋', ' ͌', ' ̃', ' ̂', ' ̌', ' ͐', ' ́', ' ̋', ' ̏', ' ̽', ' ̉', ' ͣ', ' ͤ', ' ͥ', ' ͦ', ' ͧ', ' ͨ', ' ͩ',
          ' ͪ', ' ͫ', ' ͬ', ' ͭ', ' ͮ', ' ͯ', ' ̾', ' ͛', ' ͆', ' ̚', ]
    dm = [' ̕', ' ̛', ' ̀', ' ́', ' ͘', ' ̡', ' ̢', ' ̧', ' ̨', ' ̴', ' ̵', ' ̶', ' ͜', ' ͝', ' ͞', ' ͟', ' ͠', ' ͢',
          ' ̸', ' ̷', ' ͡', ]
    letters = list(text)
    new_letters = []

    for letter in letters:
        a = letter

        if not a.isalpha():
            new_letters.append(a)
            continue

        num_accents = 0
        num_u = randint(num_accents_up[0], num_accents_up[1])
        num_d = randint(num_accents_down[0], num_accents_down[1])
        num_m = randint(num_accents_middle[0], num_accents_middle[1])
        while num_accents < max_accents_per_letter and num_u + num_m + num_d != 0:
            rand_int = randint(0, 2)
            if rand_int == 0:
                if num_u > 0:
                    a = a.strip() + du[randrange(0, len(du))].strip()
                    num_accents += 1
                    num_u -= 1
            elif rand_int == 1:
                if num_d > 0:
                    a = a.strip() + dd[randrange(0, len(dd))].strip()
                    num_d -= 1
                    num_accents += 1
            else:
                if num_m > 0:
                    a = a.strip() + dm[randrange(0, len(dm))].strip()
                    num_m -= 1
                    num_accents += 1

        new_letters.append(a)

    new_word = ''.join(new_letters)
    return new_word


async def edit_reply(result, context):
    reply = await context.get_reply_message()
    await context.edit(result)
    if reply:
        if reply.sender.is_self:
            await reply.edit(result)
            await context.delete()
