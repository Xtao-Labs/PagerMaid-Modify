""" PagerMaid launch sequence. """

from sys import path
from importlib import import_module
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from pagermaid import bot, logs, working_dir
from pagermaid.modules import module_list, plugin_list
try:
    from pagermaid.interface import server
except TypeError:
    logs.error("出错了呜呜呜 ~ Web 界面配置绑定到了一个无效地址。")
    server = None
except KeyError:
    logs.error("出错了呜呜呜 ~ 配置文件中缺少 Web 界面配置。")
    server = None


path.insert(1, f"{working_dir}/plugins")

try:
    bot.start()
except PhoneNumberInvalidError:
    print('出错了呜呜呜 ~ 输入的电话号码无效。 请确保附加国家代码。')
    exit(1)
for module_name in module_list:
    try:
        import_module("pagermaid.modules." + module_name)
    except BaseException as exception:
        logs.info(f"模块 {module_name} 加载出错: {type(exception)}: {exception}")
for plugin_name in plugin_list:
    try:
        import_module("plugins." + plugin_name)
    except BaseException as exception:
        logs.info(f"模块 {plugin_name} 加载出错: {exception}")
        plugin_list.remove(plugin_name)
if server is not None:
    import_module("pagermaid.interface")
logs.info("PagerMaid-Modify 已启动，在任何聊天中输入 -help 以获得帮助消息。")
bot.run_until_disconnected()
if server is not None:
    server.stop()
