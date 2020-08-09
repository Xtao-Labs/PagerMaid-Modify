""" Module to automate message deletion. """

from asyncio import sleep
from telethon.errors.rpcbaseerrors import BadRequestError
from pagermaid import log
from pagermaid.listener import listener


@listener(is_plugin=False, outgoing=True, command="prune",
          description="以此命令回复某条消息，将删除最新一条消息至该条消息之间的所有消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能会触发删除消息过快限制。（非群组管理员只删除自己的消息）")
async def prune(context):
    """ Purge every single message after the message you replied to. """
    if not context.reply_to_msg_id:
        await context.edit("出错了呜呜呜 ~ 没有回复的消息。")
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
    await log(f"批量删除了 {str(count)} 条消息。")
    notification = await send_prune_notify(context, count, count)
    await sleep(.5)
    await notification.delete()


@listener(is_plugin=False, outgoing=True, command="selfprune",
          description="删除当前对话您发送的特定数量的消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能会触发删除消息过快限制。入群消息非管理员无法删除。（倒序）当数字足够大时即可实现删除所有消息。",
          parameters="<数量>")
async def selfprune(context):
    """ Deletes specific amount of messages you sent. """
    if not len(context.parameter) == 1:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    try:
        count = int(context.parameter[0])
        await context.delete()
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    count_buffer = 0
    async for message in context.client.iter_messages(context.chat_id, from_user="me"):
        if count_buffer == count:
            break
        await message.delete()
        count_buffer += 1
    await log(f"批量删除了自行发送的 {str(count_buffer)} / {str(count)} 条消息。")
    notification = await send_prune_notify(context, count_buffer, count)
    await sleep(.5)
    await notification.delete()


@listener(is_plugin=False, outgoing=True, command="yourprune",
          description="删除当前对话您回复用户所发送的特定数量的消息。限制：基于消息 ID 的 1000 条消息，大于 1000 条可能会触发删除消息过快限制。（倒序、需要删除消息权限）当数字足够大时即可实现删除所有消息。",
          parameters="<数量>")
async def yourprune(context):
    """ Deletes specific amount of messages someone sent. """
    if not context.reply_to_msg_id:
        await context.edit("出错了呜呜呜 ~ 没有回复的消息。")
        return
    target = await context.get_reply_message()
    if not len(context.parameter) == 1:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    try:
        count = int(context.parameter[0])
        await context.delete()
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    except:
        pass
    count_buffer = 0
    async for message in context.client.iter_messages(context.chat_id, from_user=target.from_id):
        if count_buffer == count:
            break
        await message.delete()
        count_buffer += 1
    await log(f"批量删除了回复用户所发送的 {str(count_buffer)} / {str(count)} 条消息。")
    notification = await send_prune_notify(context, count_buffer, count)
    await sleep(.5)
    await notification.delete()


@listener(is_plugin=False, outgoing=True, command="del",
          description="删除当前对话您回复的那条消息。（需要回复一条消息）")
async def delete(context):
    """ Deletes the message you replied to. """
    target = await context.get_reply_message()
    if context.reply_to_msg_id:
        try:
            await target.delete()
            await context.delete()
            await log("删除了一条消息。")
        except BadRequestError:
            await context.edit("出错了呜呜呜 ~ 缺少删除此消息的权限。")
    else:
        await context.delete()


async def send_prune_notify(context, count_buffer, count):
    return await context.client.send_message(
        context.chat_id,
        "删除了 "
        + str(count_buffer) + " / " + str(count)
        + " 条消息。"
    )
