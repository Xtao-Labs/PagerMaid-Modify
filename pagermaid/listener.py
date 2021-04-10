""" PagerMaid event listener. """

import sys, sentry_sdk, re

from telethon import events
from telethon.errors import MessageTooLongError
from distutils2.util import strtobool
from traceback import format_exc
from time import gmtime, strftime, time
from telethon.events import StopPropagation
from pagermaid import bot, config, help_messages, logs
from pagermaid.utils import attach_report, lang


def noop(*args, **kw):
    pass


def listener(**args):
    """ Register an event listener. """
    command = args.get('command', None)
    description = args.get('description', None)
    parameters = args.get('parameters', None)
    pattern = args.get('pattern', None)
    diagnostics = args.get('diagnostics', True)
    ignore_edited = args.get('ignore_edited', False)
    is_plugin = args.get('is_plugin', True)
    if command is not None:
        if command in help_messages:
            raise ValueError(f"{lang('error_prefix')} {lang('command')} \"{command}\" {lang('has_reg')}")
        pattern = fr"^-{command}(?: |$)([\s\S]*)"
    if pattern is not None and not pattern.startswith('(?i)'):
        args['pattern'] = f"(?i){pattern}"
    else:
        args['pattern'] = pattern
    if 'ignore_edited' in args:
        del args['ignore_edited']
    if 'command' in args:
        del args['command']
    if 'diagnostics' in args:
        del args['diagnostics']
    if 'description' in args:
        del args['description']
    if 'parameters' in args:
        del args['parameters']
    if 'is_plugin' in args:
        del args['is_plugin']

    def decorator(function):

        async def handler(context):
            try:
                try:
                    parameter = context.pattern_match.group(1).split(' ')
                    if parameter == ['']:
                        parameter = []
                    context.parameter = parameter
                    context.arguments = context.pattern_match.group(1)
                except BaseException:
                    context.parameter = None
                    context.arguments = None
                await function(context)
            except StopPropagation:
                raise StopPropagation
            except MessageTooLongError:
                await context.edit(lang('too_long'))
            except BaseException as e:
                exc_info = sys.exc_info()[1]
                exc_format = format_exc()
                try:
                    await context.edit(lang('run_error'))
                except BaseException:
                    pass
                if not diagnostics:
                    return
                if strtobool(config['error_report']):
                    report = f"# Generated: {strftime('%H:%M %d/%m/%Y', gmtime())}. \n" \
                             f"# ChatID: {str(context.chat_id)}. \n" \
                             f"# UserID: {str(context.sender_id)}. \n" \
                             f"# Message: \n-----BEGIN TARGET MESSAGE-----\n" \
                             f"{context.text}\n-----END TARGET MESSAGE-----\n" \
                             f"# Traceback: \n-----BEGIN TRACEBACK-----\n" \
                             f"{str(exc_format)}\n-----END TRACEBACK-----\n" \
                             f"# Error: \"{str(exc_info)}\". \n"
                    await attach_report(report, f"exception.{time()}.pagermaid", None,
                                        "Error report generated.")
                    try:
                        sentry_sdk.set_context("Target",
                                               {"ChatID": str(context.chat_id), "UserID": str(context.sender_id),
                                                "Msg": context.text})
                        sentry_sdk.set_tag('com', re.findall("\w+", str.lower(context.text.split()[0]))[0])
                        sentry_sdk.capture_exception(e)
                    except:
                        logs.info(
                            lang('report_error')
                        )

        if not ignore_edited:
            bot.add_event_handler(handler, events.MessageEdited(**args))
        bot.add_event_handler(handler, events.NewMessage(**args))

        return handler

    if not is_plugin and 'disabled_cmd' in config:
        if config['disabled_cmd'].count(command) != 0:
            return noop

    if description is not None and command is not None:
        if parameters is None:
            parameters = ""
        help_messages.update({
            f"{command}": f"**{lang('use_method')}:** `-{command} {parameters}`\
            \n{description}"
        })

    return decorator
