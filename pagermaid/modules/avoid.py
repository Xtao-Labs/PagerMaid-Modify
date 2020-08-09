""" PagerMaid module for different ways to avoid users. """

from pagermaid import redis, log, redis_status
from pagermaid.listener import listener


@listener(is_plugin=False, outgoing=True, command="ghost",
          description="开启对话的自动已读，需要 Redis",
          parameters="<true|false|status>")
async def ghost(context):
    """ Toggles ghosting of a user. """
    if not redis_status():
        await context.edit("出错了呜呜呜 ~ Redis 好像离线了，无法执行命令。")
        return
    if len(context.parameter) != 1:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    myself = await context.client.get_me()
    self_user_id = myself.id
    if context.parameter[0] == "true":
        if context.chat_id == self_user_id:
            await context.edit("在？为什么要在收藏夹里面用？")
            return
        redis.set("ghosted.chat_id." + str(context.chat_id), "true")
        await context.delete()
        await log(f"已成功将 ChatID {str(context.chat_id)} 添加到自动已读对话列表中。")
    elif context.parameter[0] == "false":
        if context.chat_id == self_user_id:
            await context.edit("在？为什么要在收藏夹里面用？")
            return
        try:
            redis.delete("ghosted.chat_id." + str(context.chat_id))
        except:
            await context.edit("emm...当前对话不存在于自动已读对话列表中。")
            return
        await context.delete()
        await log(f"已成功将 ChatID {str(context.chat_id)} 从自动已读对话列表中移除。")
    elif context.parameter[0] == "status":
        if redis.get("ghosted.chat_id." + str(context.chat_id)):
            await context.edit("emm...当前对话存在于自动已读对话列表中。")
        else:
            await context.edit("emm...当前对话不存在于自动已读对话列表中。")
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")


@listener(is_plugin=False, outgoing=True, command="deny",
          description="拒绝聊天功能，需要 redis",
          parameters="<true|false|status>")
async def deny(context):
    """ Toggles denying of a user. """
    if not redis_status():
        await context.edit("出错了呜呜呜 ~ Redis 离线，无法运行。")
        return
    if len(context.parameter) != 1:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    myself = await context.client.get_me()
    self_user_id = myself.id
    if context.parameter[0] == "true":
        if context.chat_id == self_user_id:
            await context.edit("在？为什么要在收藏夹里面用？")
            return
        redis.set("denied.chat_id." + str(context.chat_id), "true")
        await context.delete()
        await log(f"ChatID {str(context.chat_id)} 已被添加到自动拒绝对话列表中。")
    elif context.parameter[0] == "false":
        if context.chat_id == self_user_id:
            await context.edit("在？为什么要在收藏夹里面用？")
            return
        redis.delete("denied.chat_id." + str(context.chat_id))
        await context.delete()
        await log(f"ChatID {str(context.chat_id)} 已从自动拒绝对话列表中移除。")
    elif context.parameter[0] == "status":
        if redis.get("denied.chat_id." + str(context.chat_id)):
            await context.edit("emm...当前对话已被加入自动拒绝对话列表中。")
        else:
            await context.edit("emm...当前对话已从自动拒绝对话列表移除。")
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")


@listener(is_plugin=False, incoming=True, ignore_edited=True)
async def set_read_acknowledgement(context):
    """ Event handler to infinitely read ghosted messages. """
    if not redis_status():
        return
    if redis.get("ghosted.chat_id." + str(context.chat_id)):
        await context.client.send_read_acknowledge(context.chat_id)


@listener(is_plugin=False, incoming=True, ignore_edited=True)
async def message_removal(context):
    """ Event handler to infinitely delete denied messages. """
    if not redis_status():
        return
    if redis.get("denied.chat_id." + str(context.chat_id)):
        await context.delete()
