""" The help module. """

from os import listdir
from pagermaid import help_messages
from pagermaid.utils import lang
from pagermaid.listener import listener, config


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
                                         f"[{lang('help_source')}](https://t.me/PagerMaid_Modify)")


@listener(is_plugin=False, outgoing=True, command="lang",
          description=lang('lang_des'))
async def lang_change(context):
    to_lang = context.arguments
    from_lang = config["application_language"]
    dir, ldir = listdir('languages/built-in'), []
    for i in dir:
        if not i.find('yml') == -1:
            ldir.append(i[:-4])
    with open('config.yml') as f:
        file = f.read()
    if to_lang in ldir:
        file = file.replace(f'application_language: "{from_lang}"', f'application_language: "{to_lang}"')
        with open('config.yml', 'w') as f:
            f.write(file)
        await context.edit(f"{lang('lang_change_to')} {to_lang}, {lang('lang_reboot')}")
        await context.client.disconnect()
    else:
        await context.edit(f'{lang("lang_current_lang")} {config["application_language"]}\n\n{lang("lang_all_lang")}{"，".join(ldir)}')
