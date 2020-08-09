""" QR Code related utilities. """

from os import remove
from pyqrcode import create
from pyzbar.pyzbar import decode
from PIL import Image
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import obtain_message, upload_attachment


@listener(is_plugin=False, outgoing=True, command="genqr",
          description="生成 QR Code 。",
          parameters="<string>")
async def genqr(context):
    """ Generate QR codes. """
    reply_id = context.reply_to_msg_id
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    await context.edit("生成QR码中。。。")
    try:
        create(message, error='L', mode='binary').png('qr.webp', scale=6)
    except UnicodeEncodeError:
        await context.edit("出错了呜呜呜 ~ 解析目标消息中的字符出现错误。")
        return
    await upload_attachment("qr.webp", context.chat_id, reply_id)
    remove("qr.webp")
    await context.delete()
    await log(f"为 `{message}` 生成了一张 QR 码。")


@listener(is_plugin=False, outgoing=True, command="parseqr",
          description="回复一张 QR 码进行解析并发送 QR 码内容。")
async def parseqr(context):
    """ Parse attachment of replied message as a QR Code and output results. """
    success = False
    target_file_path = await context.client.download_media(
        await context.get_reply_message()
    )
    if not target_file_path:
        await context.edit("出错了呜呜呜 ~ 回复的消息中没有附件。")
        return
    try:
        message = str(decode(Image.open(target_file_path))[0].data)[2:][:-1]
        success = True
        await context.edit(f"**内容: **\n"
                           f"`{message}`")
    except IndexError:
        await context.edit("出错了呜呜呜 ~ 回复的附件不是 QR 码。")
        message = None
    if success:
        await log(f"已解析一张带有 QR 码的消息，内容： `{message}`.")
    remove(target_file_path)
