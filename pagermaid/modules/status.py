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


@listener(is_plugin=False, outgoing=True, command="sysinfo",
          description="通过 neofetch 检索系统信息。")
async def sysinfo(context):
    """ Retrieve system information via neofetch. """
    await context.edit("加载系统信息中 . . .")
    result = await execute("neofetch --config none --stdout")
    await context.edit(f"`{result}`")


@listener(is_plugin=False, outgoing=True, command="fortune",
          description="读取 fortune cookies 信息。")
async def fortune(context):
    """ Reads a fortune cookie. """
    result = await execute("fortune")
    if result == "/bin/sh: fortune: command not found":
        await context.edit("`出错了呜呜呜 ~ 此系统上没有 fortune cookies`")
        return
    await context.edit(result)


@listener(is_plugin=False, outgoing=True, command="fbcon",
          description="拍摄当前绑定的帧缓冲控制台的屏幕截图。")
async def tty(context):
    """ Screenshots a TTY and prints it. """
    await context.edit("拍摄帧缓冲控制台的屏幕截图中 . . .")
    reply_id = context.message.reply_to_msg_id
    result = await execute("fbdump | convert - image.png")
    if result == "/bin/sh: fbdump: command not found":
        await context.edit("出错了呜呜呜 ~ 此系统上没有安装 fbdump")
        remove("image.png")
        return
    if result == "/bin/sh: convert: command not found":
        await context.edit("出错了呜呜呜 ~ 此系统上没有安装 ImageMagick")
        remove("image.png")
        return
    if result == "Failed to open /dev/fb0: Permission denied":
        await context.edit("出错了呜呜呜 ~ 运行 PagerMaid-Modify 的用户不在视频组中。")
        return
    if not await upload_attachment("./image.png", context.chat_id, reply_id,
                                   caption="绑定的帧缓冲区的屏幕截图。",
                                   preview=False, document=False):
        await context.edit("出错了呜呜呜 ~ 由于发生意外错误，导致文件生成失败。请确保已安装 apt 包 fbcat 和 imagemagick，且你的机器有显卡。")
        return
    await context.delete()
    try:
        remove("./image.png")
    except:
        pass
    await log("Screenshot of binded framebuffer console taken.")


@listener(is_plugin=False, outgoing=True, command="status",
          description="输出 PagerMaid-Modify 的运行状态。")
async def status(context):
    database = "Connected" if redis_status() else "Disconnected"
    await context.edit(
        f"**PagerMaid-Modify 运行状态** \n"
        f"主机名: `{uname().node}` \n"
        f"主机平台: `{platform}` \n"
        f"Kernel 版本: `{uname().release}` \n"
        f"Python 版本: `{python_version()}` \n"
        f"Library 版本: `{telethon_version.__version__}` \n"
        f"数据库状态: `{'Connected' if redis_status() else 'Disconnected'}`"
    )


@listener(is_plugin=False, outgoing=True, command="speedtest",
          description="执行 speedtest 脚本并发送结果。")
async def speedtest(context):
    """ Tests internet speed using speedtest. """
    await context.edit("执行测试脚本 . . .")
    test = Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    await context.edit(
        f"**Speedtest** \n"
        f"Upload: `{unit_convert(result['upload'])}` \n"
        f"Download: `{unit_convert(result['download'])}` \n"
        f"Latency: `{result['ping']}` \n"
        f"Timestamp: `{result['timestamp']}`"
    )


@listener(is_plugin=False, outgoing=True, command="connection",
          description="显示运行 PagerMaid-Modify 的服务器和 Telegram 服务器之间的连接信息。")
async def connection(context):
    """ Displays connection information between PagerMaid and Telegram. """
    datacenter = await context.client(functions.help.GetNearestDcRequest())
    await context.edit(
        f"**连接信息** \n"
        f"国家: `{datacenter.country}` \n"
        f"连接到的数据中心: `{datacenter.this_dc}` \n"
        f"最近的数据中心: `{datacenter.nearest_dc}`"
    )


@listener(is_plugin=False, outgoing=True, command="ping",
          description="计算运行 PagerMaid-Modify 的服务器和 Telegram 服务器之间的延迟。")
async def ping(context):
    """ Calculates latency between PagerMaid and Telegram. """
    start = datetime.now()
    await context.edit("Pong!")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await context.edit(f"Pong!|{duration}")


@listener(is_plugin=False, outgoing=True, command="topcloud",
          description="生成一张资源占用的词云图片。")
async def topcloud(context):
    """ Generates a word cloud of resource-hungry processes. """
    await context.edit("生成图片中 . . .")
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
    await context.edit("正在上传图片中 . . .")
    await context.client.send_file(
        context.chat_id,
        "cloud.png",
        reply_to=None,
        caption="正在运行的进程。"
    )
    remove("cloud.png")
    await context.delete()
    await log("生成了一张资源占用的词云图片。")


def unit_convert(byte):
    """ Converts byte into readable formats. """
    power = 2 ** 10
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
