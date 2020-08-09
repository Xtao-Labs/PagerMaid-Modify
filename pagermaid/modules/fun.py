""" Fun related chat utilities. """

from asyncio import sleep
from random import choice, random, randint, randrange, seed
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from cowpy import cow
from pagermaid import module_dir
from pagermaid.listener import listener
from pagermaid.utils import owoify, execute, random_gen, obtain_message


@listener(is_plugin=False, outgoing=True, command="animate",
          description="使用消息制作文本动画。",
          parameters="<message>")
async def animate(context):
    """ Make a text animation using a message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
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
          description="通过编辑消息来制作打字动画。会产生大量操作记录！",
          parameters="<message>")
async def teletype(context):
    """ Makes a typing animation via edits to the message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
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
        await context.edit(buffer)
        await sleep(interval)


@listener(is_plugin=False, outgoing=True, command="mock",
          description="通过怪异的大写字母来嘲笑人们。",
          parameters="<message>")
async def mock(context):
    """ Mock people with weird capitalization. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
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
          description="加宽字符串中的每个字符。",
          parameters="<message>")
async def widen(context):
    """ Widens every character in a string. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
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
                await context.edit("此消息已被加宽。")
                return
            await context.delete()


@listener(is_plugin=False, outgoing=True, command="fox",
          description="使用狐狸来让您的消息看起来不那么完整",
          parameters="<message>")
async def fox(context):
    """ Makes a fox scratch your message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    result = corrupt(" ".join(message).lower())
    await edit_reply(result, context)


@listener(is_plugin=False, outgoing=True, command="owo",
          description="将消息转换为OwO。",
          parameters="<message>")
async def owo(context):
    """ Makes messages become OwO. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    result = owoify(message)
    await edit_reply(result, context)


@listener(is_plugin=False, outgoing=True, command="flip",
          description="翻转消息。",
          parameters="<message>")
async def flip(context):
    """ Flip flops the message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    result = message[::-1]
    await edit_reply(result, context)


@listener(is_plugin=False, outgoing=True, command="ship",
          description="生成随机基友，也支持指定目标。",
          parameters="<username> <username>")
async def ship(context):
    """ Ship randomly generated members. """
    await context.edit("生成基友中 . . .")
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
            await context.edit("出错了呜呜呜 ~ 获取用户时出错。")
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
            await context.edit("出错了呜呜呜 ~ 获取用户时出错。")
            return
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    await context.edit(f"**恭喜两位（（（**\n"
                       f"[{target_1.first_name}](tg://user?id={target_1.id}) + "
                       f"[{target_2.first_name}](tg://user?id={target_2.id}) = ❤️")


@listener(is_plugin=False, outgoing=True, command="rng",
          description="生成具有特定长度的随机字符串。",
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
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    await context.edit("出错了呜呜呜 ~ 无效的参数。")


@listener(is_plugin=False, outgoing=True, command="aaa",
          description="发送一条包含 a 和 A 的消息",
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
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    await context.edit("出错了呜呜呜 ~ 无效的参数。")


@listener(is_plugin=False, outgoing=True, command="asciiart",
          description="为指定的字符串生成ASCII文字。",
          parameters="<string>")
async def asciiart(context):
    """ Generates ASCII art of specified string. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    result = await execute(f"figlet -f {module_dir}/assets/graffiti.flf '{message}'")
    await context.edit(f"```\n{result}\n```")


@listener(is_plugin=False, outgoing=True, command="tuxsay",
          description="生成一条看起来像企鹅说话的 ASCII 艺术消息",
          parameters="<message>")
async def tuxsay(context):
    """ Generates ASCII art of Tux saying a specific message. """
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    result = cow.Tux().milk(message)
    await context.edit(f"```\n{result}\n```")


@listener(is_plugin=False, outgoing=True, command="coin",
          description="扔硬币。")
async def coin(context):
    """ Throws a coin. """
    await context.edit("扔硬币中 . . .")
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
        await context.edit("我丢了硬币")
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
