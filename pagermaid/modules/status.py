""" PagerMaid module that contains utilities related to system status. """

from os import remove, popen
from datetime import datetime
from speedtest import Speedtest
from telethon import functions
from platform import python_version, uname
from wordcloud import WordCloud
from telethon import version as telethon_version
from sys import platform
from re import sub
from pathlib import Path
from pagermaid import log, config, redis_status
from pagermaid.utils import execute, upload_attachment
from pagermaid.listener import listener
from pagermaid.utils import lang


@listener(is_plugin=False, outgoing=True, command="sysinfo",
          description=lang('sysinfo_des'))
async def sysinfo(context):
    """ Retrieve system information via neofetch. """
    await context.edit(lang('sysinfo_loading'))
    result = await execute("neofetch --config none --stdout")
    await context.edit(f"`{result}`")


@listener(is_plugin=False, outgoing=True, command="fortune",
          description=lang('fortune_des'))
async def fortune(context):
    """ Reads a fortune cookie. """
    result = await execute("fortune")
    if result == "/bin/sh: fortune: command not found":
        await context.edit(lang('fortune_not_exist'))
        return
    await context.edit(result)


@listener(is_plugin=False, outgoing=True, command="fbcon",
          description=lang('fbcon_des'))
async def tty(context):
    """ Screenshots a TTY and prints it. """
    await context.edit(lang('fbcon_processing'))
    reply_id = context.message.reply_to_msg_id
    result = await execute("fbdump | convert - image.png")
    if result == "/bin/sh: fbdump: command not found":
        await context.edit(lang('fbcon_no_fbdump'))
        remove("image.png")
        return
    if result == "/bin/sh: convert: command not found":
        await context.edit(lang('fbcon_no_ImageMagick'))
        remove("image.png")
        return
    if result == "Failed to open /dev/fb0: Permission denied":
        await context.edit(lang('fbcon_no_permission'))
        return
    if not await upload_attachment("./image.png", context.chat_id, reply_id,
                                   caption=lang('fbcon_caption'),
                                   preview=False, document=False):
        await context.edit(lang('fbcon_error'))
        return
    await context.delete()
    try:
        remove("./image.png")
    except:
        pass
    await log("Screenshot of binded framebuffer console taken.")


@listener(is_plugin=False, outgoing=True, command="status",
          description=lang('status_des'))
async def status(context):
    database = lang('status_online') if redis_status() else lang('status_offline')
    text = (f"**{lang('status_hint')}** \n"
        f"{lang('status_name')}: `{uname().node}` \n"
        f"{lang('status_platform')}: `{platform}` \n"
        f"{lang('status_release')}: `{uname().release}` \n"
        f"{lang('status_python')}: `{python_version()}` \n"
        f"{lang('status_telethon')}: `{telethon_version.__version__}` \n"
        f"{lang('status_db')}: `{database}`"
    )
    await context.edit(text)
    dialogs = await context.client.get_dialogs()
    dialogs = len(dialogs)
    text += f"\n{lang('status_dialogs')}: `{dialogs}`"
    await context.edit(text)


@listener(is_plugin=False, outgoing=True, command="speedtest",
          description=lang('speedtest_des'))
async def speedtest(context):
    """ Tests internet speed using speedtest. """
    await context.edit(lang('speedtest_processing'))
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    des = (
        f"**Speedtest** \n"
        f"Server: `{result['server']['name']}` \n"
        f"Upload: `{unit_convert(result['upload'])}` \n"
        f"Download: `{unit_convert(result['download'])}` \n"
        f"Latency: `{result['ping']}` \n"
        f"Timestamp: `{result['timestamp']}`"
    )
    await context.client.send_file(context.chat.id, result['share'], caption=des)
    await context.delete()


@listener(is_plugin=False, outgoing=True, command="connection",
          description=lang('connection_des'))
async def connection(context):
    """ Displays connection information between PagerMaid and Telegram. """
    datacenter = await context.client(functions.help.GetNearestDcRequest())
    await context.edit(
        f"**{lang('connection_hint')}** \n"
        f"{lang('connection_country')}: `{datacenter.country}` \n"
        f"{lang('connection_dc')}: `{datacenter.this_dc}` \n"
        f"{lang('connection_nearest_dc')}: `{datacenter.nearest_dc}`"
    )


@listener(is_plugin=False, outgoing=True, command="ping",
          description=lang('ping_des'))
async def ping(context):
    """ Calculates latency between PagerMaid and Telegram. """
    start = datetime.now()
    await context.edit("Pong!")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await context.edit(f"Pong!|{duration}")


@listener(is_plugin=False, outgoing=True, command="topcloud",
          description=lang('topcloud_des'))
async def topcloud(context):
    """ Generates a word cloud of resource-hungry processes. """
    await context.edit(lang('topcloud_processing'))
    command_list = []
    if not Path('/usr/bin/top').is_symlink():
        output = str(await execute("top -b -n 1")).split("\n")[7:]
    else:
        output = str(await execute("top -b -n 1")).split("\n")[4:]
    for line in output[:-1]:
        line = sub(r'\s+', ' ', line).strip()
        fields = line.split(" ")
        try:
            if fields[11].count("/") > 0:
                command = fields[11].split("/")[0]
            else:
                command = fields[11]

            cpu = float(fields[8].replace(",", "."))
            mem = float(fields[9].replace(",", "."))

            if command != "top":
                command_list.append((command, cpu, mem))
        except BaseException:
            pass
    command_dict = {}
    for command, cpu, mem in command_list:
        if command in command_dict:
            command_dict[command][0] += cpu
            command_dict[command][1] += mem
        else:
            command_dict[command] = [cpu + 1, mem + 1]

    resource_dict = {}

    for command, [cpu, mem] in command_dict.items():
        resource_dict[command] = (cpu ** 2 + mem ** 2) ** 0.5

    width, height = None, None
    try:
        width, height = ((popen("xrandr | grep '*'").read()).split()[0]).split("x")
        width = int(width)
        height = int(height)
    except BaseException:
        pass
    if not width or not height:
        width = int(config['width'])
        height = int(config['height'])
    background = config['background']
    margin = int(config['margin'])

    cloud = WordCloud(
        background_color=background,
        width=width - 2 * int(margin),
        height=height - 2 * int(margin)
    ).generate_from_frequencies(resource_dict)

    cloud.to_file("cloud.png")
    await context.edit(lang('highlight_uploading'))
    await context.client.send_file(
        context.chat_id,
        "cloud.png",
        reply_to=None,
        caption=lang('topcloud_caption')
    )
    remove("cloud.png")
    await context.delete()
    await log(lang('topcloud_success'))


def unit_convert(byte):
    """ Converts byte into readable formats. """
    power = 1000
    zero = 0
    units = {
        0: '',
        1: 'Kb/s',
        2: 'Mb/s',
        3: 'Gb/s',
        4: 'Tb/s'}
    while byte > power:
        byte /= power
        zero += 1
    return f"{round(byte, 2)} {units[zero]}"
