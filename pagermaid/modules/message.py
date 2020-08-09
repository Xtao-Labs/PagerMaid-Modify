""" Message related utilities. """

import requests
import json
from telethon.tl.functions.messages import DeleteChatUserRequest
from telethon.tl.functions.channels import LeaveChannelRequest, GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.errors.rpcerrorlist import ChatIdInvalidError
from distutils2.util import strtobool
from pagermaid import bot, log, config
from pagermaid.listener import listener


@listener(is_plugin=False, outgoing=True, command="id",
          description="获取一条消息的各种信息。")
async def userid(context):
    """ Query the UserID of the sender of the message you replied to. """
    message = await context.get_reply_message()
    text = "Message ID: `" + str(context.message.id) + "`\n\n"
    text += "**Chat**\nid:`" + str(context.chat_id) + "`\n"
    if context.is_private:
        try:
            text += "first_name: `" + context.chat.first_name + "`\n"
        except TypeError:
            text += "**死号**\n"
        if context.chat.last_name:
            text += "last_name: `" + context.chat.last_name + "`\n"
        if context.chat.username:
            text += "username: @" + context.chat.username + "\n"
        if context.chat.lang_code:
            text += "lang_code: `" + context.chat.lang_code + "`\n"
    if context.is_group or context.is_channel:
        text += "title: `" + context.chat.title + "`\n"
        if context.chat.username:
            text += "username: @" + context.chat.username + "\n"
        text += "date: `" + str(context.chat.date) + "`\n"
    if message:
        text += "\n以下是被回复消息的信息\nMessage ID: `" + str(message.id) + "`\n\n**User**\nid: `" + str(message.sender.id) + "`"
        if message.sender.bot:
            text += "\nis_bot: 是"
        try:
            text += "\nfirst_name: `" + message.sender.first_name + "`"
        except TypeError:
            text += "\n**死号**"
        if message.sender.last_name:
            text += "\nlast_name: `" + message.sender.last_name + "`"
        if message.sender.username:
            text += "\nusername: @" + message.sender.username
        if message.sender.lang_code:
            text += "\nlang_code: `" + message.sender.lang_code + "`"
        if message.forward:
            if str(message.forward.chat_id).startswith('-100'):
                text += "\n\n**Forward From Channel**\nid: `" + str(
                    message.forward.chat_id) + "`\ntitle: `" + message.forward.chat.title + "`"
                if message.forward.chat.username:
                    text += "\nusername: @" + message.forward.chat.username
                text += "\nmessage_id: `" + str(message.forward.channel_post) + "`"
                if message.forward.post_author:
                    text += "\npost_author: `" + message.forward.post_author + "`"
                text += "\ndate: `" + str(message.forward.date) + "`"
            else:
                if message.forward.sender:
                    text += "\n\n**Forward From User**\nid: `" + str(
                        message.forward.sender_id) + "`"
                    if message.forward.sender.bot:
                        text += "\nis_bot: 是"
                    try:
                        text += "\nfirst_name: `" + message.forward.sender.first_name + "`"
                    except TypeError:
                        text += "\n**死号**"
                    if message.forward.sender.last_name:
                        text += "\nlast_name: `" + message.forward.sender.last_name + "`"
                    if message.forward.sender.username:
                        text += "\nusername: @" + message.forward.sender.username
                    if message.forward.sender.lang_code:
                        text += "\nlang_code: `" + message.forward.sender.lang_code + "`"
                    text += "\ndate: `" + str(message.forward.date) + "`"
    await context.edit(text)


@listener(is_plugin=False, outgoing=True, command="uslog",
          description="转发一条消息到日志。",
          parameters="<string>")
async def uslog(context):
    """ Forwards a message into log group """
    if strtobool(config['log']):
        if context.reply_to_msg_id:
            reply_msg = await context.get_reply_message()
            await reply_msg.forward_to(int(config['log_chatid']))
        elif context.arguments:
            await log(context.arguments)
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
            return
        await context.edit("已记录。")
    else:
        await context.edit("出错了呜呜呜 ~ 日志记录已禁用。")


@listener(is_plugin=False, outgoing=True, command="log",
          description="静默转发一条消息到日志。",
          parameters="<string>")
async def log(context):
    """ Forwards a message into log group """
    if strtobool(config['log']):
        if context.reply_to_msg_id:
            reply_msg = await context.get_reply_message()
            await reply_msg.forward_to(int(config['log_chatid']))
        elif context.arguments:
            await log(context.arguments)
        else:
            await context.edit("出错了呜呜呜 ~ 无效的参数。")
            return
        await context.delete()
    else:
        await context.edit("出错了呜呜呜 ~ 日志记录已禁用。")


@listener(is_plugin=False, outgoing=True, command="re",
          description="在当前会话复读回复的消息。（需要回复一条消息）",
          parameters="<次数>")
async def re(context):
    """ Forwards a message into this group """
    reply = await context.get_reply_message()
    if reply:
        if context.arguments == '':
            num = 1
        else:
            try:
                num = int(context.arguments)
                if num > 100:
                    await context.edit('呜呜呜出错了...这个数字太大惹')
                    return True
            except:
                await context.edit('呜呜呜出错了...可能参数包含了数字以外的符号')
                return True
        await context.delete()
        for nums in range(0, num):
            await reply.forward_to(int(context.chat_id))
    else:
        await context.edit("出错了呜呜呜 ~ 您好像没有回复一条消息。")


@listener(is_plugin=False, outgoing=True, command="leave",
          description="说 “再见” 然后离开会话。")
async def leave(context):
    """ It leaves you from the group. """
    if context.is_group:
        await context.edit("贵群真是浪费我的时间，再见。")
        try:
            await bot(DeleteChatUserRequest(chat_id=context.chat_id,
                                            user_id=context.sender_id
                                            ))
        except ChatIdInvalidError:
            await bot(LeaveChannelRequest(context.chat_id))
    else:
        await context.edit("出错了呜呜呜 ~ 当前聊天似乎不是群聊。")


@listener(is_plugin=False, outgoing=True, command="meter2feet",
          description="将米转换为英尺。",
          parameters="<meters>")
async def meter2feet(context):
    """ Convert meter to feet. """
    if not len(context.parameter) == 1:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    meter = float(context.parameter[0])
    feet = meter / .3048
    await context.edit(f"将 {str(meter)} 米装换为了 {str(feet)} 英尺。")


@listener(is_plugin=False, outgoing=True, command="feet2meter",
          description="将英尺转换为米。",
          parameters="<feet>")
async def feet2meter(context):
    """ Convert feet to meter. """
    if not len(context.parameter) == 1:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    feet = float(context.parameter[0])
    meter = feet * .3048
    await context.edit(f"将 {str(feet)} 英尺转换为了 {str(meter)} 米。")


@listener(is_plugin=False, outgoing=True, command="hitokoto",
          description="每日一言")
async def hitokoto(context):
    """ Get hitokoto.cn """
    hitokoto_while = 1
    try:
        hitokoto_json = json.loads(requests.get("https://v1.hitokoto.cn/?charset=utf-8").content.decode("utf-8"))
    except (ValueError):
        while hitokoto_while < 10:
            hitokoto_while += 1
            try:
                hitokoto_json = json.loads(requests.get("https://v1.hitokoto.cn/?charset=utf-8").content.decode("utf-8"))
                break
            except:
                continue
    if hitokoto_json['type'] == 'a':
        hitokoto_type = '动画'
    elif hitokoto_json['type'] == 'b':
        hitokoto_type = '漫画'
    elif hitokoto_json['type'] == 'c':
        hitokoto_type = '游戏'
    elif hitokoto_json['type'] == 'd':
        hitokoto_type = '文学'
    elif hitokoto_json['type'] == 'e':
        hitokoto_type = '原创'
    elif hitokoto_json['type'] == 'f':
        hitokoto_type = '来自网络'
    elif hitokoto_json['type'] == 'g':
        hitokoto_type = '其他'
    elif hitokoto_json['type'] == 'h':
        hitokoto_type = '影视'
    elif hitokoto_json['type'] == 'i':
        hitokoto_type = '诗词'
    elif hitokoto_json['type'] == 'j':
        hitokoto_type = '网易云'
    elif hitokoto_json['type'] == 'k':
        hitokoto_type = '哲学'
    elif hitokoto_json['type'] == 'l':
        hitokoto_type = '抖机灵'
    await context.edit(f"{hitokoto_json['hitokoto']} - {hitokoto_json['from']}（{str(hitokoto_type)}）")


@listener(is_plugin=False, outgoing=True, command="source",
          description="显示原始 PagerMaid git 存储库的URL。")
async def source(context):
    """ Outputs the git repository URL. """
    await context.edit("https://git.stykers.moe/scm/~stykers/pagermaid.git")


@listener(is_plugin=False, outgoing=True, command="site",
          description="显示原始 PagerMaid 项目主页的URL。")
async def site(context):
    """ Outputs the site URL. """
    await context.edit("https://katonkeyboard.moe/pagermaid.html")
