""" PagerMaid launch sequence. """

from sys import path
from importlib import import_module
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from pagermaid import bot, logs, working_dir
from pagermaid.utils import lang
from pagermaid.modules import module_list, plugin_list
try:
    from pagermaid.interface import server
except TypeError:
    logs.error(lang('web_TypeError'))
    server = None
except KeyError:
    logs.error(lang('web_KeyError'))
    server = None


path.insert(1, f"{working_dir}/plugins")

try:
    bot.start()
except PhoneNumberInvalidError:
    print(lang('PhoneNumberInvalidError'))
    exit(1)
for module_name in module_list:
    try:
        import_module("pagermaid.modules." + module_name)
    except BaseException as exception:
        logs.info(f"{lang('module')} {module_name} {lang('error')}: {type(exception)}: {exception}")
for plugin_name in plugin_list:
    try:
        import_module("plugins." + plugin_name)
    except BaseException as exception:
        logs.info(f"{lang('module')} {plugin_name} {lang('error')}: {exception}")
        plugin_list.remove(plugin_name)
if server is not None:
    import_module("pagermaid.interface")
logs.info(lang('start'))
bot.run_until_disconnected()
if server is not None:
    try:
        server.stop()
    except AttributeError:
        pass
