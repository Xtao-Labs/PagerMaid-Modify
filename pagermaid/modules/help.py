""" The help module. """

from pagermaid import help_messages
from pagermaid.listener import listener


@listener(is_plugin=False, outgoing=True, command="help",
          description="显示命令列表或单个命令的帮助。",
          parameters="<命令>")
async def help(context):
    """ The help command,"""
    if context.arguments:
        if context.arguments in help_messages:
            await context.edit(str(help_messages[context.arguments]))
        else:
            await context.edit("无效的参数")
    else:
        result = "**命令列表: \n**"
        for command in sorted(help_messages, reverse=False):
            result += "`" + str(command)
            result += "`, "
        await context.edit(result[:-2] + "\n**发送 \"-help <命令>\" 以查看特定命令的帮助。** [源代码](https://t.me/PagerMaid_Modify)")
