""" Module to automate message deletion. """

from asyncio import sleep
from telethon.errors.rpcbaseerrors import BadRequestError
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import lang


@listener(is_plugin=False, outgoing=True, command="prune",
          description=lang('prune_des'))
async def prune(context):
    """ Purge every single message after the message you replied to. """
    if not context.reply_to_msg_id:
        await context.edit(lang('not_reply'))
        return
    input_chat = await context.get_input_chat()
    messages = []
    count = 0
    async for message in context.client.iter_messages(input_chat, min_id=context.reply_to_msg_id):
        messages.append(message)
        count += 1
        messages.append(context.reply_to_msg_id)
        if len(messages) == 100:
            await context.client.delete_messages(input_chat, messages)
            messages = []

    if messages:
        await context.client.delete_messages(input_chat, messages)
    await log(f"{lang('prune_hint1')} {str(count)} {lang('prune_hint2')}")
    notification = await send_prune_notify(context, count, count)
    await sleep(.5)
    await notification.delete()


@listener(is_plugin=False, outgoing=True, command="selfprune",
          description=lang('sp_des'),
          parameters=lang('sp_parameters'))
async def selfprune(context):
    """ Deletes specific amount of messages you sent. """
    if not len(context.parameter) == 1:
        await context.edit(lang('arg_error'))
        return
    try:
        count = int(context.parameter[0])
        await context.delete()
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    count_buffer = 0
    async for message in context.client.iter_messages(context.chat_id, from_user="me"):
        if count_buffer == count:
            break
        await message.delete()
        count_buffer += 1
    await log(f"{lang('prune_hint1')}{lang('sp_hint')} {str(count_buffer)} / {str(count)} {lang('prune_hint2')}")
    notification = await send_prune_notify(context, count_buffer, count)
    await sleep(.5)
    await notification.delete()


@listener(is_plugin=False, outgoing=True, command="yourprune",
          description=lang('yp_des'),
          parameters=lang('sp_parameters'))
async def yourprune(context):
    """ Deletes specific amount of messages someone sent. """
    if not context.reply_to_msg_id:
        await context.edit(lang('not_reply'))
        return
    target = await context.get_reply_message()
    if not len(context.parameter) == 1:
        await context.edit(lang('arg_error'))
        return
    try:
        count = int(context.parameter[0])
        await context.delete()
    except ValueError:
        await context.edit(lang('arg_error'))
        return
    except:
        pass
    count_buffer = 0
    async for message in context.client.iter_messages(context.chat_id, from_user=target.from_id):
        if count_buffer == count:
            break
        await message.delete()
        count_buffer += 1
    await log(f"{lang('prune_hint1')}{lang('yp_hint')} {str(count_buffer)} / {str(count)} {lang('prune_hint2')}")
    notification = await send_prune_notify(context, count_buffer, count)
    await sleep(.5)
    await notification.delete()


@listener(is_plugin=False, outgoing=True, command="del",
          description=lang('del_des'))
async def delete(context):
    """ Deletes the message you replied to. """
    target = await context.get_reply_message()
    if context.reply_to_msg_id:
        try:
            await target.delete()
            await context.delete()
            await log(lang('del_notification'))
        except BadRequestError:
            await context.edit(lang('del_BadRequestError'))
    else:
        await context.delete()


async def send_prune_notify(context, count_buffer, count):
    return await context.client.send_message(
        context.chat_id,
        lang('spn_deleted')
        + str(count_buffer) + " / " + str(count)
        + lang('prune_hint2')
    )
