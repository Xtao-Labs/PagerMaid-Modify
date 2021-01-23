""" PagerMaid module to manage plugins. """

import json
from re import search, I
from requests import get
from os import remove, rename, chdir, path
from os.path import exists
from shutil import copyfile, move
from glob import glob
from pagermaid import log, working_dir
from pagermaid.listener import listener
from pagermaid.utils import upload_attachment
from pagermaid.modules import plugin_list as active_plugins, __list_plugins


@listener(is_plugin=False, outgoing=True, command="apt", diagnostics=False,
          description="用于管理安装到 PagerMaid-Modify 的插件。",
          parameters="{update|search|show|status|install|remove|enable|disable|upload} <插件名称/文件>")
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
        elif len(context.parameter) == 2:
            plugin_name = context.parameter[1]
            plugin_online = \
            json.loads(get("https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/list.json").content)[
                'list']
            if exists(f"{plugin_directory}version.json"):
                with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                    version_json = json.load(f)
                try:
                    plugin_version = version_json[plugin_name]
                except:
                    plugin_version = False
            else:
                temp_dict = {}
                with open(f"{plugin_directory}version.json", 'w') as f:
                    json.dump(temp_dict, f)
                plugin_version = False
            for i in plugin_online:
                if i['name'] == plugin_name:
                    if plugin_version:
                        if (float(i['version']) - float(plugin_version)) <= 0:
                            await context.edit(f"插件 {plugin_name} 为最新版本，无需更新。")
                            return
                        else:
                            file_path = plugin_name + ".py"
                            plugin_content = get(
                                f"https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/{plugin_name}.py").content
                            with open(file_path, 'wb') as f:
                                f.write(plugin_content)
                            with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                                version_json = json.load(f)
                            version_json[plugin_name] = i['version']
                            with open(f"{plugin_directory}version.json", 'w') as f:
                                json.dump(version_json, f)
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
                        file_path = plugin_name + ".py"
                        plugin_content = get(
                            f"https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/{plugin_name}.py").content
                        with open(file_path, 'wb') as f:
                            f.write(plugin_content)
                        with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                            version_json = json.load(f)
                        version_json[plugin_name] = i['version']
                        with open(f"{plugin_directory}version.json", 'w') as f:
                            json.dump(version_json, f)
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
            await context.edit(f"错误：没有找到插件 {plugin_name} 。")
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
    elif context.parameter[0] == "remove":
        if len(context.parameter) == 2:
            if exists(f"{plugin_directory}{context.parameter[1]}.py"):
                remove(f"{plugin_directory}{context.parameter[1]}.py")
                with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                    version_json = json.load(f)
                version_json[context.parameter[1]] = '0.0'
                with open(f"{plugin_directory}version.json", 'w') as f:
                    json.dump(version_json, f)
                await context.edit(f"成功删除插件 {context.parameter[1]}, PagerMaid-Modify 正在重新启动。")
                await log(f"删除插件 {context.parameter[1]}.")
                await context.client.disconnect()
            elif exists(f"{plugin_directory}{context.parameter[1]}.py.disabled"):
                remove(f"{plugin_directory}{context.parameter[1]}.py.disabled")
                with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                    version_json = json.load(f)
                version_json[context.parameter[1]] = '0.0'
                with open(f"{plugin_directory}version.json", 'w') as f:
                    json.dump(version_json, f)
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
    elif context.parameter[0] == "update":
        unneed_update = "无需更新："
        need_update = "\n已更新："
        need_update_list = []
        if not exists(f"{plugin_directory}version.json"):
            await context.edit("安装一个仓库内插件再试试？")
            return
        with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
            version_json = json.load(f)
        plugin_online = \
        json.loads(get("https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/list.json").content)['list']
        for key, value in version_json.items():
            if value == "0.0":
                continue
            for i in plugin_online:
                if key == i['name']:
                    if (float(i['version']) - float(value)) <= 0:
                        unneed_update += "\n`" + key + "`：Ver  " + value
                    else:
                        need_update_list.extend([key])
                        need_update += "\n`" + key + "`：Ver  " + value + " --> Ver  " + i['version']
                    continue
        if unneed_update == "无需更新：":
            unneed_update = ''
        if need_update == "\n已更新：":
            need_update = ''
        if unneed_update == '' and need_update == '':
            await context.edit("不如去安装一些插件？")
        else:
            if len(need_update_list) == 0:
                await context.edit('正在读取云端插件列表...完成\n正在读取本地插件版本信息...完成\n**没有需要更新的插件。**')
            else:
                print(6)
                await context.edit('正在读取云端插件列表...完成\n正在读取本地插件版本信息...完成\n正在更新插件...')
                plugin_directory = f"{working_dir}/plugins/"
                for i in need_update_list:
                    file_path = i + ".py"
                    plugin_content = get(
                        f"https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/{i}.py").content
                    with open(file_path, 'wb') as f:
                        f.write(plugin_content)
                    with open(f"{plugin_directory}version.json", 'r', encoding="utf-8") as f:
                        version_json = json.load(f)
                    for m in plugin_online:
                        if m['name'] == i:
                            version_json[i] = m['version']
                    with open(f"{plugin_directory}version.json", 'w') as f:
                        json.dump(version_json, f)
                    if exists(f"{plugin_directory}{file_path}"):
                        remove(f"{plugin_directory}{file_path}")
                        move(file_path, plugin_directory)
                    elif exists(f"{plugin_directory}{file_path}.disabled"):
                        remove(f"{plugin_directory}{file_path}.disabled")
                        move(file_path, f"{plugin_directory}{file_path}.disabled")
                    else:
                        move(file_path, plugin_directory)
                await context.edit('正在读取云端插件列表...完成\n正在读取本地插件版本信息...完成\n' + need_update)
    elif context.parameter[0] == "search":
        if len(context.parameter) == 1:
            await context.edit("没插件名我怎么搜索？")
        elif len(context.parameter) == 2:
            search_result = []
            plugin_name = context.parameter[1]
            plugin_online = \
            json.loads(get("https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/list.json").content)[
                'list']
            for i in plugin_online:
                if search(plugin_name, i['name'], I):
                    search_result.extend(['`' + i['name'] + '` / `' + i['version'] + '`\n  ' + i['des-short']])
            if len(search_result) == 0:
                await context.edit("未在插件仓库中搜索到相关插件。")
            else:
                await context.edit('以下是插件仓库的搜索结果：\n\n' + '\n\n'.join(search_result))
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
    elif context.parameter[0] == "show":
        if len(context.parameter) == 1:
            await context.edit("没插件名我怎么显示？")
        elif len(context.parameter) == 2:
            search_result = ''
            plugin_name = context.parameter[1]
            plugin_online = \
            json.loads(get("https://raw.githubusercontent.com/xtaodada/PagerMaid_Plugins/master/list.json").content)[
                'list']
            for i in plugin_online:
                if plugin_name == i['name']:
                    if i['supported']:
                        search_support = '仍在周期中'
                    else:
                        search_support = '已弃疗'
                    search_result = '插件名：`' + i['name'] + '`\n版本：`Ver  ' + i['version'] + '`\n分类：`' + i[
                        'section'] + '`\n作者：`' + \
                                    i['maintainer'] + '`\n大小：`' + i['size'] + '`\n支持周期：' + search_support + '\n说明：' + i[
                                        'des-short'] + '\n\n' + i['des']
                    break
            if search_result == '':
                await context.edit("未在插件仓库中搜索到相关插件。")
            else:
                await context.edit(search_result)
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
