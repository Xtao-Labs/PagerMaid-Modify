""" System related utilities for PagerMaid to integrate into the system. """

from platform import node
from getpass import getuser
from os import geteuid
from requests import head
from asyncio import sleep
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError
from pagermaid import log, bot
from pagermaid.listener import listener
from pagermaid.utils import attach_log, execute, lang
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError
from telethon.tl.functions.messages import ImportChatInviteRequest


@listener(is_plugin=False, outgoing=True, command="sh",
          description=lang('sh_des'),
          parameters=lang('sh_parameters'))
async def sh(context):
    """ Use the command-line from Telegram. """
    user = getuser()
    command = context.arguments
    hostname = node()
    if context.is_channel and not context.is_group:
        await context.edit(lang('sh_channel'))
        return

    if not command:
        await context.edit(lang('arg_error'))
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
    await log(f"{lang('sh_success')}: `{command}`")


@listener(is_plugin=False, outgoing=True, command="restart", diagnostics=False,
          description=lang('restart_des'))
async def restart(context):
    """ To re-execute PagerMaid. """
    if not context.text[0].isalpha():
        await context.edit(lang('restart_processing'))
        await log(lang('restart_log'))
        await context.client.disconnect()


@listener(is_plugin=False, outgoing=True, command="trace",
          description=lang('trace_des'),
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
        await context.edit(lang('trace_processing'))
        result = str("")
        for url in url_tracer(url):
            count = 0
            if result:
                result += " ↴\n" + url
            else:
                result = url
            if count == 128:
                result += f"\n\n{lang('trace_over128')}"
                break
        if result:
            if len(result) > 4096:
                await context.edit(lang('translate_tg_limit_uploading_file'))
                await attach_log(result, context.chat_id, "output.log", context.id)
                return
            await context.edit(
                f"{lang('trace_re')}:\n"
                f"{result}"
            )
            await log(f"Traced redirects of {context.arguments}.")
        else:
            await context.edit(lang('trace_http_error'))
    else:
        await context.edit(lang('arg_error'))


@listener(is_plugin=False, outgoing=True, command="chat",
          description=lang('chat_des'))
async def contact_chat(context):
    """ join a chatroom. """
    message = lang('chat_message')
    try:
        await bot(ImportChatInviteRequest('KFUDIlXq9nWYVwPW4QugXw'))
    except UserAlreadyParticipantError:
        await context.edit(f'{lang("chat_already_join1")} [Pagermaid-Modify](https://github.com/xtaodada/PagerMaid-Modify/) {lang("chat_already_join2")}')
        return
    except:
        await context.edit(lang('chat_error'))
        return True
    await sleep(3)
    await context.client.send_message(
        -1001441461877,
        message
    )
    notification = await context.edit(f'{lang("chat_join_success")} [Pagermaid-Modify](https://github.com/xtaodada/PagerMaid-Modify/) {lang("chat_already_join2")}。')
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
