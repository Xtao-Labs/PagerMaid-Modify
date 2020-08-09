from time import time
from uuid import uuid1
from os.path import exists
from requests import get
from pagermaid import bot, working_dir
from pagermaid.listener import listener


@listener(is_plugin=False, incoming=True, ignore_edited=True)
async def status(context):
    if exists(f"{working_dir}/data/time"):
        with open(f"{working_dir}/data/time", "r") as f:  # 打开文件
            status_time = float(f.read().replace("\n", ""))  # 读取文件
    else:
        status_time = 0
    if status_time + 120 < time():
        with open(f"{working_dir}/data/time", "w") as f:
            f.write(str(time()))
        if not exists(f"{working_dir}/data/uuid"):
            with open(f"{working_dir}/data/uuid","w") as f:
                f.write(str(uuid1()))
        with open(f"{working_dir}/data/uuid", "r") as f:  # 打开文件
                uuid  = f.read()  # 读取文件
        try:
            get("https://xtaolink.cn/git/staton.php?id=" + uuid)
        except:
            pass
    else:
        pass
