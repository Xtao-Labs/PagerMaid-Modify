""" System related utilities for PagerMaid to integrate into the system. """

from platform import node
from getpass import getuser
from os import geteuid
from requests import head
from asyncio import sleep
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError
from pagermaid import log, bot
from pagermaid.listener import listener
from pagermaid.utils import attach_log, execute
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
from telethon.tl.functions.messages import ImportChatInviteRequest


@listener(is_plugin=False, outgoing=True, command="sh",
          description="在 Telegram 上远程执行 Shell 命令。",
          parameters="<命令>")
async def sh(context):
    """ Use the command-line from Telegram. """
    user = getuser()
    command = context.arguments
    hostname = node()
    if context.is_channel and not context.is_group:
        await context.edit("`出错了呜呜呜 ~ 当前 PagerMaid-Modify 的配置禁止在频道中执行 Shell 命令。`")
        return

    if not command:
        await context.edit("`出错了呜呜呜 ~ 无效的参数。`")
        return

    if geteuid() == 0:
        await context.edit(
            f"`{user}`@{hostname} ~"
            f"\n> `#` {command}"
        )
    else:
        await context.edit(
            f"`{user}`@{hostname} ~"
            f"\n> `$` {command}"
        )

    result = await execute(command)

    if result:
        if len(result) > 4096:
            await attach_log(result, context.chat_id, "output.log", context.id)
            return

        if geteuid() == 0:
            await context.edit(
                f"`{user}`@{hostname} ~"
                f"\n> `#` {command}"
                f"\n`{result}`"
            )
        else:
            await context.edit(
                f"`{user}`@{hostname} ~"
                f"\n> `$` {command}"
                f"\n`{result}`"
            )
    else:
        return
    await log(f"远程执行 Shell 命令： `{command}`")


@listener(is_plugin=False, outgoing=True, command="restart", diagnostics=False,
          description="使 PagerMaid-Modify 重新启动")
async def restart(context):
    """ To re-execute PagerMaid. """
    if not context.text[0].isalpha():
        await context.edit("尝试重新启动 PagerMaid-Modify 。")
        await log("PagerMaid-Modify 重新启动。")
        await context.client.disconnect()


@listener(is_plugin=False, outgoing=True, command="trace",
          description="跟踪 URL 的重定向。",
          parameters="<url>")
async def trace(context):
    """ Trace URL redirects. """
    url = context.arguments
    reply = await context.get_reply_message()
    if reply:
        url = reply.text
    if url:
        if url.startswith("https://") or url.startswith("http://"):
            pass
        else:
            url = "https://" + url
        await context.edit("跟踪重定向中 . . .")
        result = str("")
        for url in url_tracer(url):
            count = 0
            if result:
                result += " ↴\n" + url
            else:
                result = url
            if count == 128:
                result += "\n\n出错了呜呜呜 ~ 超过128次重定向，正在中止!"
                break
        if result:
            if len(result) > 4096:
                await context.edit("输出超出限制，正在附加文件。")
                await attach_log(result, context.chat_id, "output.log", context.id)
                return
            await context.edit(
                "重定向:\n"
                f"{result}"
            )
            await log(f"Traced redirects of {context.arguments}.")
        else:
            await context.edit(
                "出错了呜呜呜 ~ 发出 HTTP 请求时出了点问题。"
            )
    else:
        await context.edit("无效的参数。")


@listener(is_plugin=False, outgoing=True, command="contact",
          description="向 Kat 发送消息。",
          parameters="<message>")
async def contact(context):
    """ Sends a message to Kat. """
    await context.edit("请点击 `[这里](https://t.me/PagerMaid_Modify)` 进入.",
                       parse_mode="markdown")
    message = "Hi, I would like to report something about PagerMaid."
    if context.arguments:
        message = context.arguments
    await context.client.send_message(
        503691334,
        message
    )


@listener(is_plugin=False, outgoing=True, command="chat",
          description="加入 Pagermaid-Modify 用户群。")
async def contact_chat(context):
    """ join a chatroom. """
    message = "大家好，我是新人。"
    try:
        await bot(ImportChatInviteRequest('KFUDIlXq9nWYVwPW4QugXw'))
    except UserAlreadyParticipantError:
        await context.edit('您早已成功加入 [Pagermaid-Modify](https://github.com/xtaodada/PagerMaid-Modify/) 用户群。')
        return
    except:
        await context.edit('出错了呜呜呜 ~ 请尝试手动加入 @PagerMaid_Modify')
        return True
    await sleep(3)
    await context.client.send_message(
        -1001441461877,
        message
    )
    notification = await context.edit('您已成功加入 [Pagermaid-Modify](https://github.com/xtaodada/PagerMaid-Modify/) 用户群。')
    await sleep(5)
    await notification.delete()


def url_tracer(url):
    """ Method to trace URL redirects. """
    while True:
        yield url
        try:
            response = head(url)
        except MissingSchema:
            break
        except InvalidURL:
            break
        except ConnectionError:
            break
        if 300 < response.status_code < 400:
            url = response.headers['location']
        else:
            break
