from pyrogram import __version__
from main import bot, reg_handler, des_handler, par_handler, redis
from plugins.system import execute
from platform import python_version, uname
from sys import platform
from speedtest import Speedtest
from datetime import datetime
from pathlib import Path
from re import sub
from os import remove, popen
from wordcloud import WordCloud
from getpass import getuser
from socket import gethostname
from time import time
from psutil import boot_time, virtual_memory, disk_partitions
from shutil import disk_usage
from subprocess import Popen, PIPE


async def sysinfo(message, args, origin_text):
    """ Retrieve system information via neofetch. """
    await message.edit("加载系统信息中 . . .")
    if platform == 'win32':
        await message.edit(neofetch_win(), parse_mode='html')
        return
    result = await execute("neofetch --config none --stdout")
    await message.edit(f"`{result}`")


async def status(message, args, origin_text):
    redis_con = '在线' if redis_status() else "离线"
    dialogs_count = await bot.get_dialogs_count()
    await message.edit(
        f"**PagerMaid-Modify Beta 运行状态** \n"
        f"主机名: `{uname().node}` \n"
        f"主机平台: `{platform}` \n"
        f"Kernel 版本: `{uname().release}` \n"
        f"Python 版本: `{python_version()}` \n"
        f"Pyrogram 版本: `{__version__}` \n"
        f"Redis 状态: `{redis_con}`\n"
        f"对话总数: `{dialogs_count}`"
    )


async def speedtest(message, args, origin_text):
    """ Tests internet speed using speedtest. """
    await message.edit("执行测试脚本 . . .")
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
    await bot.send_photo(message.chat.id, result['share'], caption=des)
    await message.delete()


async def ping(message, args, origin_text):
    """ Calculates latency between PagerMaid and Telegram. """
    start = datetime.now()
    await message.edit("Pong!")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await message.edit(f"Pong!|{duration}")


async def topcloud(message, args, origin_text):
    """ Generates a word cloud of resource-hungry processes. """
    if platform == 'win32':
        await message.edit(f"此命令暂不支持 win 系统。")
        return
    await message.edit("生成图片中 . . .")
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
        width = int("1920")
        height = int("1080")
    background = "#101010"
    margin = int("20")

    cloud = WordCloud(
        background_color=background,
        width=width - 2 * int(margin),
        height=height - 2 * int(margin)
    ).generate_from_frequencies(resource_dict)

    cloud.to_file("cloud.png")
    await message.edit("正在上传图片中 . . .")
    await bot.send_photo(
        message.chat.id,
        "cloud.png",
        caption="正在运行的进程。"
    )
    remove("cloud.png")
    await message.delete()


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


def redis_status():
    try:
        redis.ping()
        return True
    except BaseException:
        return False


def wmic(command: str):
    """ Fetch the wmic command to cmd """
    try:
        p = Popen(command.split(" "), stdout=PIPE)
    except FileNotFoundError:
        print("WMIC.exe was not found... Make sure 'C:\Windows\System32\wbem' is added to PATH.")

    stdout, stderror = p.communicate()

    output = stdout.decode("gbk", "ignore")
    lines = output.split("\r\r")
    lines = [g.replace("\n", "").replace("  ", "") for g in lines if len(g) > 2]
    return lines


def get_uptime():
    """ Get the device uptime """
    delta = round(time() - boot_time())

    hours, remainder = divmod(int(delta), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    def includeS(text: str, num: int):
        return f"{num} {text}{'' if num == 1 else 's'}"

    d = includeS("day", days)
    h = includeS("hour", hours)
    m = includeS("minute", minutes)
    s = includeS("second", seconds)

    if days:
        output = f"{d}, {h}, {m} and {s}"
    elif hours:
        output = f"{h}, {m} and {s}"
    elif minutes:
        output = f"{m} and {s}"
    else:
        output = s

    return output


def readable(num, suffix='B'):
    """ Convert Bytes into human readable formats """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_ram():
    """ Get RAM used/free/total """
    ram = virtual_memory()
    used = readable(ram.used)
    total = readable(ram.total)

    percent_used = round(ram.used / ram.total * 100, 2)

    return f"{used} / {total} ({percent_used}%)"


def partitions():
    """ Find the disk partitions on current OS """
    parts = disk_partitions()
    listparts = []

    for g in parts:
        try:
            total, used, free = disk_usage(g.device)
            percent_used = round(used / total * 100, 2)
            listparts.append(f"      {g.device[:2]} {readable(used)} / {readable(total)} ({percent_used}%)")
        except PermissionError:
            continue

    return listparts


def neofetch_win():
    user_name = getuser()
    host_name = gethostname()
    os = wmic("wmic os get Caption")[-1].replace("Microsoft ", "")
    uptime = get_uptime()
    mboard_name = wmic("wmic baseboard get Manufacturer")
    mboard_module = wmic("wmic baseboard get product")
    try:
        mboard = f"{mboard_name[-1]} ({mboard_module[-1]})"
    except IndexError:
        mboard = "Unknown..."
    cpu = wmic("wmic cpu get name")[-1]
    gpu = wmic("wmic path win32_VideoController get name")
    gpu = [f'     {g.strip()}' for g in gpu[1:]][0].strip()
    ram = get_ram()
    disks = '\n'.join(partitions())
    text = f'<code>{user_name}@{host_name}\n---------\nOS: {os}\nUptime: {uptime}\n' \
           f'Motherboard: {mboard}\nCPU: {cpu}\nGPU: {gpu}\nMemory: {ram}\n' \
           f'Disk:\n{disks}</code>'
    return text


reg_handler('sysinfo', sysinfo)
reg_handler('status', status)
reg_handler('speedtest', speedtest)
reg_handler('ping', ping)
reg_handler('topcloud', topcloud)
des_handler('sysinfo', '通过 neofetch 检索系统信息。')
des_handler('status', '输出 PagerMaid-Modify 的运行状态。')
des_handler('speedtest', '执行 speedtest 脚本并发送结果。')
des_handler('ping', '计算运行 PagerMaid-Modify 的服务器和 Telegram 服务器之间的延迟。')
des_handler('topcloud', '生成一张资源占用的词云图片。')
par_handler('sysinfo', '')
par_handler('status', '')
par_handler('speedtest', '')
par_handler('ping', '')
par_handler('topcloud', '')
