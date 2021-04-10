""" The help module. """

from pagermaid import help_messages
from pagermaid.utils import lang
from pagermaid.listener import listener


@listener(is_plugin=False, outgoing=True, command="help",
          description=lang('help_des'),
          parameters=f"<{lang('command')}>")
async def help(context):
    """ The help command,"""
    if context.arguments:
        if context.arguments in help_messages:
            await context.edit(str(help_messages[context.arguments]))
        else:
            await context.edit(lang('arg_error'))
    else:
        result = f"**{lang('help_list')}: \n**"
        for command in sorted(help_messages, reverse=False):
            result += "`" + str(command)
            result += "`, "
        await context.edit(result[:-2] + f"\n**{lang('help_send')} \"-help <{lang('command')}>\" {lang('help_see')}** "
                                         f"[{lang('源代码')}](https://t.me/PagerMaid_Modify)")
