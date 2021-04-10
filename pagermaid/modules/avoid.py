""" PagerMaid module for different ways to avoid users. """

from pagermaid import redis, log, redis_status
from pagermaid.utils import lang
from pagermaid.listener import listener


@listener(is_plugin=False, outgoing=True, command="ghost",
          description=lang('ghost_des'),
          parameters="<true|false|status>")
async def ghost(context):
    """ Toggles ghosting of a user. """
    if not redis_status():
        await context.edit(f"{lang('error_prefix')}{lang('redis_dis')}")
        return
    if len(context.parameter) != 1:
        await context.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        return
    myself = await context.client.get_me()
    self_user_id = myself.id
    if context.parameter[0] == "true":
        if context.chat_id == self_user_id:
            await context.edit(lang('ghost_e_mark'))
            return
        redis.set("ghosted.chat_id." + str(context.chat_id), "true")
        await context.delete()
        await log(f"{lang('ghost_set_f')} ChatID {str(context.chat_id)} {lang('ghost_set_l')}")
    elif context.parameter[0] == "false":
        if context.chat_id == self_user_id:
            await context.edit(lang('ghost_e_mark'))
            return
        try:
            redis.delete("ghosted.chat_id." + str(context.chat_id))
        except:
            await context.edit(lang('ghost_e_noexist'))
            return
        await context.delete()
        await log(f"{lang('ghost_set_f')} ChatID {str(context.chat_id)} {lang('ghost_cancel')}")
    elif context.parameter[0] == "status":
        if redis.get("ghosted.chat_id." + str(context.chat_id)):
            await context.edit(lang('ghost_e_exist'))
        else:
            await context.edit(lang('ghost_e_noexist'))
    else:
        await context.edit(f"{lang('error_prefix')}{lang('arg_error')}")


@listener(is_plugin=False, outgoing=True, command="deny",
          description=lang('deny_des'),
          parameters="<true|false|status>")
async def deny(context):
    """ Toggles denying of a user. """
    if not redis_status():
        await context.edit(f"{lang('error_prefix')}{lang('redis_dis')}")
        return
    if len(context.parameter) != 1:
        await context.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        return
    myself = await context.client.get_me()
    self_user_id = myself.id
    if context.parameter[0] == "true":
        if context.chat_id == self_user_id:
            await context.edit(lang('ghost_e_mark'))
            return
        redis.set("denied.chat_id." + str(context.chat_id), "true")
        await context.delete()
        await log(f"ChatID {str(context.chat_id)} {lang('deny_set')}")
    elif context.parameter[0] == "false":
        if context.chat_id == self_user_id:
            await context.edit(lang('ghost_e_mark'))
            return
        redis.delete("denied.chat_id." + str(context.chat_id))
        await context.delete()
        await log(f"ChatID {str(context.chat_id)} {lang('deny_cancel')}")
    elif context.parameter[0] == "status":
        if redis.get("denied.chat_id." + str(context.chat_id)):
            await context.edit(lang('deny_e_exist'))
        else:
            await context.edit(lang('deny_e_noexist'))
    else:
        await context.edit(f"{lang('error_prefix')}{lang('arg_error')}")


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
