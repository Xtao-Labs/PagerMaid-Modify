""" PagerMaid module for adding captions to image. """

from os import remove
from magic import Magic
from pygments import highlight as syntax_highlight
from pygments.formatters import img
from pygments.lexers import guess_lexer
from pagermaid import log, module_dir
from pagermaid.listener import listener
from pagermaid.utils import execute, upload_attachment


@listener(is_plugin=False, outgoing=True, command="convert",
          description="回复某条附件消息然后转换为图片输出")
async def convert(context):
    """ Converts image to png. """
    reply = await context.get_reply_message()
    await context.edit("正在转换中 . . .")
    target_file_path = await context.download_media()
    reply_id = context.reply_to_msg_id
    if reply:
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
    if target_file_path is None:
        await context.edit("出错了呜呜呜 ~ 回复的消息中好像没有附件。")
    result = await execute(f"{module_dir}/assets/caption.sh \"" + target_file_path +
                           "\" result.png" + " \"" + str("") +
                           "\" " + "\"" + str("") + "\"")
    if not result:
        await handle_failure(context, target_file_path)
        return
    if not await upload_attachment("result.png", context.chat_id, reply_id):
        await context.edit("出错了呜呜呜 ~ 转换期间发生了错误。")
        remove(target_file_path)
        return
    await context.delete()
    remove(target_file_path)
    remove("result.png")


@listener(is_plugin=False, outgoing=True, command="caption",
          description="将两行字幕添加到回复的图片中，字幕将分别添加到顶部和底部，字幕需要以逗号分隔。",
          parameters="<string>,<string> <image>")
async def caption(context):
    """ Generates images with captions. """
    await context.edit("正在渲染图像中 . . .")
    if context.arguments:
        if ',' in context.arguments:
            string_1, string_2 = context.arguments.split(',', 1)
        else:
            string_1 = context.arguments
            string_2 = " "
    else:
        await context.edit("出错了呜呜呜 ~ 错误的语法。")
        return
    reply = await context.get_reply_message()
    target_file_path = await context.download_media()
    reply_id = context.reply_to_msg_id
    if reply:
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
    if target_file_path is None:
        await context.edit("出错了呜呜呜 ~ 目标消息中没有附件")
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
        await context.edit("出错了呜呜呜 ~ 转换期间发生了错误。")
        remove(target_file_path)
        return
    await context.delete()
    if string_2 != " ":
        message = string_1 + "` 和 `" + string_2
    else:
        message = string_1
    remove(target_file_path)
    remove(result_file)
    await log(f"成功将字幕 `{message}` 添加到了一张图片.")


@listener(is_plugin=False, outgoing=True, command="ocr",
          description="从回复的图片中提取文本")
async def ocr(context):
    """ Extracts texts from images. """
    args = context.parameter
    try:
        psm = args[0]
    except:
        psm = '3'
    if not 0 <= int(psm) <= 13:
        await context.edit(' 呜呜呜出错了...psm 取值为 0-13')
        return
    reply = await context.get_reply_message()
    await context.edit("`正在处理图片，请稍候 . . .`")
    if reply:
        target_file_path = await context.client.download_media(
            await context.get_reply_message()
        )
    else:
        target_file_path = await context.download_media()
    if target_file_path is None:
        await context.edit("`出错了呜呜呜 ~ 回复的消息中没有附件。`")
        return
    result = await execute(f"tesseract {target_file_path} stdout")
    if not result:
        await context.edit("`出错了呜呜呜 ~ 请向原作者报告此问题。`")
        try:
            remove(target_file_path)
        except FileNotFoundError:
            pass
        return
    result = await execute(f"tesseract -c preserve_interword_spaces=1 -l chi_sim --psm {psm} \"{target_file_path}\" stdout 2>/dev/null", False)
    await context.edit(f"**以下是提取到的文字: **\n{result}")
    success = True
    remove(target_file_path)


@listener(is_plugin=False, outgoing=True, command="highlight",
          description="生成有语法高亮显示的图片。",
          parameters="<string>")
async def highlight(context):
    """ Generates syntax highlighted images. """
    if context.fwd_from:
        return
    reply = await context.get_reply_message()
    reply_id = None
    await context.edit("正在渲染图片，请稍候 . . .")
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
            await context.edit("`出错了呜呜呜 ~ 无法检索目标消息。`")
            return
    lexer = guess_lexer(message)
    formatter = img.JpgImageFormatter(style="colorful")
    result = syntax_highlight(message, lexer, formatter, outfile=None)
    await context.edit("正在上传图片中 . . .")
    await context.client.send_file(
        context.chat_id,
        result,
        reply_to=reply_id
    )
    await context.delete()


async def handle_failure(context, target_file_path):
    await context.edit("出错了呜呜呜 ~ 请向原作者报告此问题。")
    try:
        remove("result.png")
        remove(target_file_path)
    except FileNotFoundError:
        pass
