""" PagerMaid initialization. """

import sentry_sdk

from subprocess import run, PIPE
from time import time
from os import getcwd, makedirs
from os.path import exists
from sys import version_info, platform
from yaml import load, FullLoader
from shutil import copyfile
from redis import StrictRedis
from logging import getLogger, INFO, DEBUG, ERROR, StreamHandler, basicConfig
from distutils2.util import strtobool
from coloredlogs import ColoredFormatter
from telethon import TelegramClient

persistent_vars = {}
module_dir = __path__[0]
working_dir = getcwd()
config = None
help_messages = {}
logs = getLogger(__name__)
logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
logging_handler = StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))
root_logger = getLogger()
root_logger.setLevel(ERROR)
root_logger.addHandler(logging_handler)
basicConfig(level=INFO)
logs.setLevel(INFO)

try:
    config = load(open(r"config.yml"), Loader=FullLoader)
except FileNotFoundError:
    logs.fatal("出错了呜呜呜 ~ 配置文件不存在，正在生成新的配置文件。")
    copyfile(f"{module_dir}/assets/config.gen.yml", "config.yml")
    exit(1)


if strtobool(config['debug']):
    logs.setLevel(DEBUG)
else:
    logs.setLevel(INFO)


if platform == "linux" or platform == "linux2" or platform == "darwin" or platform == "freebsd7" \
        or platform == "freebsd8" or platform == "freebsdN" or platform == "openbsd6":
    logs.info(
        "将平台检测为“ " + platform + "，进入PagerMaid的早期加载过程。"
    )
else:
    logs.error(
        "出错了呜呜呜 ~ 你的平台 " + platform + " 不支持运行 PagerMaid，请在Linux或 *BSD 上启动 PagerMaid。"
    )
    exit(1)

if version_info[0] < 3 or version_info[1] < 6:
    logs.error(
        "出错了呜呜呜 ~ 请将您的 python 升级到至少3.6版。"
    )
    exit(1)

if not exists(f"{getcwd()}/data"):
    makedirs(f"{getcwd()}/data")

api_key = config['api_key']
api_hash = config['api_hash']
try:
    proxy_addr = config['proxy_addr'].strip()
    proxy_port = config['proxy_port'].strip()
    mtp_addr = config['mtp_addr'].strip()
    mtp_port = config['mtp_port'].strip()
    mtp_secret = config['mtp_secret'].strip()
except:
    proxy_addr = ''
    proxy_port = ''
    mtp_addr = ''
    mtp_port = ''
    mtp_secret = ''
try:
    redis_host = config['redis']['host']
except KeyError:
    redis_host = 'localhost'
try:
    redis_port = config['redis']['port']
except KeyError:
    redis_port = 6379
try:
    redis_db = config['redis']['db']
except KeyError:
    redis_db = 14
if api_key is None or api_hash is None:
    logs.info(
        "出错了呜呜呜 ~ 请在工作目录中放置一个有效的配置文件。"
    )
    exit(1)

if not proxy_addr == '' and not proxy_port == '':
    try:
        import socks
    except:
        pass
    bot = TelegramClient("pagermaid", api_key, api_hash, auto_reconnect=True, proxy=(socks.SOCKS5, proxy_addr, int(proxy_port)))
elif not mtp_addr == '' and not mtp_port == '' and not mtp_secret == '':
    from telethon import connection
    bot = TelegramClient("pagermaid", api_key, api_hash, auto_reconnect=True,
                         connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                         proxy=(mtp_addr, int(mtp_port), mtp_secret))
else:
    bot = TelegramClient("pagermaid", api_key, api_hash, auto_reconnect=True)
redis = StrictRedis(host=redis_host, port=redis_port, db=redis_db)


async def save_id():
    me = await bot.get_me()
    sentry_sdk.set_user({"id": me.id, "ip_address": "{{auto}}"})
    logs.info("设置用户标识成功。")


with bot:
    bot.loop.run_until_complete(save_id())


def before_send(event, hint):
    global report_time
    if time() <= report_time + 30:
        report_time = time()
        return None
    else:
        report_time = time()
        return event


report_time = time()
git_hash = run("git rev-parse --short HEAD", stdout=PIPE, shell=True).stdout.decode()
sentry_sdk.init(
    "https://969892b513374f75916aaac1014aa7c2@o416616.ingest.sentry.io/5312335",
    traces_sample_rate=1.0,
    release=git_hash,
    before_send=before_send,
    environment="production",
    integrations=[RedisIntegration()]
)


def redis_status():
    try:
        redis.ping()
        return True
    except BaseException:
        return False


async def log(message):
    logs.info(
        message.replace('`', '\"')
    )
    if not strtobool(config['log']):
        return
    await bot.send_message(
        int(config['log_chatid']),
        message
    )
