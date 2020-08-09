""" PagerMaid module to manage plugins. """

from os import remove, rename, chdir, path
from os.path import exists
from shutil import copyfile, move
from glob import glob
from pagermaid import log, working_dir
from pagermaid.listener import listener
from pagermaid.utils import upload_attachment
from pagermaid.modules import plugin_list as active_plugins, __list_plugins


@listener(is_plugin=False, outgoing=True, command="plugin", diagnostics=False,
          description="用于管理安装到 PagerMaid-Modify 的插件。",
          parameters="{status|install|remove|enable|disable|upload} <插件名称/文件>")
async def plugin(context):
    if len(context.parameter) > 2 or len(context.parameter) == 0:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    reply = await context.get_reply_message()
    plugin_directory = f"{working_dir}/plugins/"
    if context.parameter[0] == "install":
        if len(context.parameter) == 1:
            await context.edit("安装插件中 . . .")
            if reply:
                file_path = await context.client.download_media(reply)
            else:
                file_path = await context.download_media()
            if file_path is None or not file_path.endswith('.py'):
                await context.edit("出错了呜呜呜 ~ 无法从附件获取插件文件。")
                try:
                    remove(str(file_path))
                except FileNotFoundError:
                    pass
                return
            if exists(f"{plugin_directory}{file_path}"):
                remove(f"{plugin_directory}{file_path}")
                move(file_path, plugin_directory)
            elif exists(f"{plugin_directory}{file_path}.disabled"):
                remove(f"{plugin_directory}{file_path}.disabled")
                move(file_path, f"{plugin_directory}{file_path}.disabled")
            else:
                move(file_path, plugin_directory)
            await context.edit(f"插件 {path.basename(file_path)[:-3]} 已安装，PagerMaid-Modify 正在重新启动。")
            await log(f"成功安装插件 {path.basename(file_path)[:-3]}.")
            await context.client.disconnect()
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
    elif context.parameter[0] == "remove":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py"):
                remove(f"{plugin_directory}{context.parameter[1]}.py")
                await context.edit(f"成功删除插件 {context.parameter[1]}, PagerMaid-Modify 正在重新启动。")
                await log(f"删除插件 {context.parameter[1]}.")
                await context.client.disconnect()
            elif exists(f"{plugin_directory}{context.parameter[1]}.py.disabled"):
                remove(f"{plugin_directory}{context.parameter[1]}.py.disabled")
                await context.edit(f"已删除的插件 {context.parameter[1]}.")
                await log(f"已删除的插件 {context.parameter[1]}.")
            elif "/" in context.parameter[1]:
                await context.edit("出错了呜呜呜 ~ 无效的参数。")
            else:
                await context.edit("出错了呜呜呜 ~ 指定的插件不存在。")
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
    elif context.parameter[0] == "status":
        if len(context.parameter) == 1:
            inactive_plugins = sorted(__list_plugins())
            disabled_plugins = []
            if not len(inactive_plugins) == 0:
                for target_plugin in active_plugins:
                    inactive_plugins.remove(target_plugin)
            chdir("plugins/")
            for target_plugin in glob(f"*.py.disabled"):
                disabled_plugins += [f"{target_plugin[:-12]}"]
            chdir("../")
            active_plugins_string = ""
            inactive_plugins_string = ""
            disabled_plugins_string = ""
            for target_plugin in active_plugins:
                active_plugins_string += f"{target_plugin}, "
            active_plugins_string = active_plugins_string[:-2]
            for target_plugin in inactive_plugins:
                inactive_plugins_string += f"{target_plugin}, "
            inactive_plugins_string = inactive_plugins_string[:-2]
            for target_plugin in disabled_plugins:
                disabled_plugins_string += f"{target_plugin}, "
            disabled_plugins_string = disabled_plugins_string[:-2]
            if len(active_plugins) == 0:
                active_plugins_string = "`没有运行中的插件。`"
            if len(inactive_plugins) == 0:
                inactive_plugins_string = "`没有加载失败的插件。`"
            if len(disabled_plugins) == 0:
                disabled_plugins_string = "`没有关闭的插件`"
            output = f"**插件列表**\n" \
                     f"运行中: {active_plugins_string}\n" \
                     f"已关闭: {disabled_plugins_string}\n" \
                     f"加载失败: {inactive_plugins_string}"
            await context.edit(output)
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
    elif context.parameter[0] == "enable":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py.disabled"):
                rename(f"{plugin_directory}{context.parameter[1]}.py.disabled",
                       f"{plugin_directory}{context.parameter[1]}.py")
                await context.edit(f"插件 {context.parameter[1]} 已启用，PagerMaid-Modify 正在重新启动。")
                await log(f"已启用 {context.parameter[1]}.")
                await context.client.disconnect()
            else:
                await context.edit("出错了呜呜呜 ~ 指定的插件不存在。")
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
    elif context.parameter[0] == "disable":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py") is True:
                rename(f"{plugin_directory}{context.parameter[1]}.py",
                       f"{plugin_directory}{context.parameter[1]}.py.disabled")
                await context.edit(f"插件 {context.parameter[1]} 已被禁用，PagerMaid-Modify 正在重新启动。")
                await log(f"已关闭插件 {context.parameter[1]}.")
                await context.client.disconnect()
            else:
                await context.edit("出错了呜呜呜 ~ 指定的插件不存在。")
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
    elif context.parameter[0] == "upload":
        if len(context.parameter) == 2:
            file_name = f"{context.parameter[1]}.py"
            reply_id = None
            if reply:
                reply_id = reply.id
            if exists(f"{plugin_directory}{file_name}"):
                copyfile(f"{plugin_directory}{file_name}", file_name)
            elif exists(f"{plugin_directory}{file_name}.disabled"):
                copyfile(f"{plugin_directory}{file_name}.disabled", file_name)
            if exists(file_name):
                await context.edit("上传插件中 . . .")
                await upload_attachment(file_name,
                                        context.chat_id, reply_id,
                                        caption=f"PagerMaid-Modify {context.parameter[1]} plugin.")
                remove(file_name)
                await context.delete()
            else:
                await context.edit("出错了呜呜呜 ~ 指定的插件不存在。")
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
