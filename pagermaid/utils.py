""" Libraries for python modules. """

from os import remove
from os.path import exists
from emoji import get_emoji_regexp
from random import choice
from json import load as load_json
from re import sub, IGNORECASE
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from youtube_dl import YoutubeDL
from pagermaid import module_dir, bot


async def upload_attachment(file_path, chat_id, reply_id, caption=None, preview=None, document=None):
    """ Uploads a local attachment file. """
    if not exists(file_path):
        return False
    try:
        await bot.send_file(
            chat_id,
            file_path,
            reply_to=reply_id,
            caption=caption,
            link_preview=preview,
            force_document=document
        )
    except BaseException as exception:
        raise exception
    return True


async def execute(command, pass_error=True):
    """ Executes command and returns output, with the option of enabling stderr. """
    executor = await create_subprocess_shell(
        command,
        stdout=PIPE,
        stderr=PIPE
    )

    stdout, stderr = await executor.communicate()
    if pass_error:
        result = str(stdout.decode().strip()) \
                 + str(stderr.decode().strip())
    else:
        result = str(stdout.decode().strip())
    return result


async def attach_log(plaintext, chat_id, file_name, reply_id=None, caption=None):
    """ Attach plaintext as logs. """
    file = open(file_name, "w+")
    file.write(plaintext)
    file.close()
    await bot.send_file(
        chat_id,
        file_name,
        reply_to=reply_id,
        caption=caption
    )
    remove(file_name)

async def attach_report(plaintext, file_name, reply_id=None, caption=None):
    """ Attach plaintext as logs. """
    file = open(file_name, "w+")
    file.write(plaintext)
    file.close()
    try:
        await bot.send_file(
            1263764543,
            file_name,
            reply_to=reply_id,
            caption=caption
        )
    except:
        async with bot.conversation('PagerMaid_Modify_bot') as conversation:
            await conversation.send_message('/ping')
            await conversation.get_response()
            await bot.send_read_acknowledge(conversation.chat_id)
            await bot.send_file(
                1263764543,
                file_name,
                reply_to=reply_id,
                caption=caption
            )
    remove(file_name)

async def obtain_message(context):
    """ Obtains a message from either the reply message or command arguments. """
    reply = await context.get_reply_message()
    message = context.arguments
    if reply and not message:
        message = reply.text
    if not message:
        raise ValueError("出错了呜呜呜 ~ 没有成功获取到消息！")
    return message


async def random_gen(selection, length=64):
    if not isinstance(length, int):
        raise ValueError("出错了呜呜呜 ~ 长度必须是整数!")
    return await execute(f"head -c 65536 /dev/urandom | tr -dc {selection} | head -c {length} ; echo \'\'")


async def fetch_youtube_audio(url, chat_id, reply_id, string_2):
    """ Extracts and uploads audio from YouTube video. """
    youtube_dl_options = {
        'format': 'bestaudio/best',
        'outtmpl': "audio.%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    YoutubeDL(youtube_dl_options).download([url])
    if not exists("audio.mp3"):
        return False
    await bot.send_file(
         chat_id,
         "audio.mp3",
         reply_to=reply_id,
         caption=str(string_2)
    )
    remove("audio.mp3")
    return True


def owoify(text):
    """ Converts your text to OwO """
    smileys = [';;w;;', '^w^', '>w<', 'UwU', '(・`ω´・)', '(´・ω・`)']
    with open(f"{module_dir}/assets/replacements.json") as fp:
        replacements = load_json(fp)
    for expression in replacements:
        replacement = replacements[expression]
        text = sub(expression, replacement, text, flags=IGNORECASE)
    words = text.split()
    first_letter = words[0][0]
    letter_stutter = f"{first_letter}-{first_letter.lower()}-{first_letter.lower()}"
    if len(words[0]) > 1:
        words[0] = letter_stutter + words[0][1:]
    else:
        words[0] = letter_stutter
    text = " ".join(words)
    text = text.replace('L', 'W').replace('l', 'w')
    text = text.replace('R', 'W').replace('r', 'w')
    text = '! {}'.format(choice(smileys)).join(text.rsplit('!', 1))
    text = '? OwO'.join(text.rsplit('?', 1))
    text = '. {}'.format(choice(smileys)).join(text.rsplit('.', 1))
    text = f"{text} desu"
    for v in ['a', 'o', 'u', 'A', 'O', 'U']:
        if 'n{}'.format(v) in text:
            text = text.replace('n{}'.format(v), 'ny{}'.format(v))
        if 'N{}'.format(v) in text:
            text = text.replace('N{}'.format(v), 'N{}{}'.format('Y' if v.isupper() else 'y', v))
    return text


def clear_emojis(target):
    """ Removes all Emojis from provided string """
    return get_emoji_regexp().sub(u'', target)
