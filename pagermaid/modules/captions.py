""" PagerMaid module for adding captions to image. """

from os import remove
from magic import Magic
from pygments import highlight as syntax_highlight
from pygments.formatters import img
from pygments.lexers import guess_lexer
from pagermaid import log, module_dir
from pagermaid.listener import listener
from pagermaid.utils import execute, upload_attachment, lang


@listener(is_plugin=False, outgoing=True, command="convert",
          description=lang('convert_des'))
async def convert(context):
    """ Converts image to png. """
    reply = await context.get_reply_message()
    await context.edit(lang('convert_process'))
    target_file_path = await context.download_media()
    reply_id = context.reply_to_msg_id
    if reply:
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
    if target_file_path is None:
        await context.edit(lang('convert_no_file'))
    result = await execute(f"{module_dir}/assets/caption.sh \"" + target_file_path +
                           "\" result.png" + " \"" + str("") +
                           "\" " + "\"" + str("") + "\"")
    if not result:
        await handle_failure(context, target_file_path)
        return
    if not await upload_attachment("result.png", context.chat_id, reply_id):
        await context.edit(lang('convert_error'))
        remove(target_file_path)
        return
    await context.delete()
    remove(target_file_path)
    remove("result.png")


@listener(is_plugin=False, outgoing=True, command="caption",
          description=lang('caption_des'),
          parameters="<string>,<string> <image>")
async def caption(context):
    """ Generates images with captions. """
    await context.edit(lang('caption_process'))
    if context.arguments:
        if ',' in context.arguments:
            string_1, string_2 = context.arguments.split(',', 1)
        else:
            string_1 = context.arguments
            string_2 = " "
    else:
        await context.edit(lang('caption_error_grammer'))
        return
    reply = await context.get_reply_message()
    target_file_path = await context.download_media()
    reply_id = context.reply_to_msg_id
    if reply:
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
    if target_file_path is None:
        await context.edit(lang('caption_no_file'))
    if not target_file_path.endswith(".mp4"):
        result = await execute(f"{module_dir}/assets/caption.sh \"{target_file_path}\" "
                               f"{module_dir}/assets/Impact-Regular.ttf "
                               f"\"{str(string_1)}\" \"{str(string_2)}\"")
        result_file = "result.png"
    else:
        result = await execute(f"{module_dir}/assets/caption-gif.sh \"{target_file_path}\" "
                               f"{module_dir}/assets/Impact-Regular.ttf "
                               f"\"{str(string_1)}\" \"{str(string_2)}\"")
        result_file = "result.gif"
    if not result:
        await handle_failure(context, target_file_path)
        return
    if not await upload_attachment(result_file, context.chat_id, reply_id):
        await context.edit(lang('capiton_error'))
        remove(target_file_path)
        return
    await context.delete()
    if string_2 != " ":
        message = string_1 + "` 和 `" + string_2
    else:
        message = string_1
    remove(target_file_path)
    remove(result_file)
    await log(f"{lang('caption_success1')} `{message}` {lang('caption_success2')}")


@listener(is_plugin=False, outgoing=True, command="ocr",
          description=lang('ocr_des'))
async def ocr(context):
    """ Extracts texts from images. """
    args = context.parameter
    try:
        psm = args[0]
    except:
        psm = '3'
    if not 0 <= int(psm) <= 13:
        await context.edit(lang('ocr_psm_len_error'))
        return
    reply = await context.get_reply_message()
    await context.edit(lang('ocr_processing'))
    if reply:
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
    else:
        target_file_path = await context.download_media()
    if target_file_path is None:
        await context.edit(lang('ocr_no_file'))
        return
    result = await execute(f"tesseract {target_file_path} stdout")
    if not result:
        await context.edit(lang('ocr_no_result'))
        try:
            remove(target_file_path)
        except FileNotFoundError:
            pass
        return
    result = await execute(f"tesseract -c preserve_interword_spaces=1 -l chi_sim --psm {psm} \"{target_file_path}\" stdout 2>/dev/null", False)
    await context.edit(f"**{lang('ocr_result_hint')}: **\n{result}")
    success = True
    remove(target_file_path)


@listener(is_plugin=False, outgoing=True, command="highlight",
          description=lang('highlight_des'),
          parameters="<string>")
async def highlight(context):
    """ Generates syntax highlighted images. """
    if context.fwd_from:
        return
    reply = await context.get_reply_message()
    reply_id = None
    await context.edit(lang('highlight_processing'))
    if reply:
        reply_id = reply.id
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
        if target_file_path is None:
            message = reply.text
        else:
            if Magic(mime=True).from_file(target_file_path) != 'text/plain':
                message = reply.text
            else:
                with open(target_file_path, 'r') as file:
                    message = file.read()
            remove(target_file_path)
    else:
        if context.arguments:
            message = context.arguments
        else:
            await context.edit(lang('highlight_no_file'))
            return
    lexer = guess_lexer(message)
    formatter = img.JpgImageFormatter(style="colorful")
    result = syntax_highlight(message, lexer, formatter, outfile=None)
    await context.edit(lang('highlight_uploading'))
    await context.client.send_file(
        context.chat_id,
        result,
        reply_to=reply_id
    )
    await context.delete()


async def handle_failure(context, target_file_path):
    await context.edit(lang('handle_failure_error'))
    try:
        remove("result.png")
        remove(target_file_path)
    except FileNotFoundError:
        pass
