""" QR Code related utilities. """

from os import remove
from pyqrcode import create
from pyzbar.pyzbar import decode
from PIL import Image
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import obtain_message, upload_attachment, lang


@listener(is_plugin=False, outgoing=True, command="genqr",
          description=lang('genqr_des'),
          parameters="<string>")
async def genqr(context):
    """ Generate QR codes. """
    reply_id = context.reply_to_msg_id
    try:
        message = await obtain_message(context)
    except ValueError:
        await context.edit(lang('error_prefix'))
        return
    await context.edit(lang('genqr_process'))
    try:
        create(message, error='L', mode='binary').png('qr.webp', scale=6)
    except UnicodeEncodeError:
        await context.edit(f"{lang('error_prefix')}{lang('genqr_e_encode')}")
        return
    await upload_attachment("qr.webp", context.chat_id, reply_id)
    remove("qr.webp")
    await context.delete()
    await log(f"`{message}` {lang('genqr_ok')}")


@listener(is_plugin=False, outgoing=True, command="parseqr",
          description=lang('parseqr_des'))
async def parseqr(context):
    """ Parse attachment of replied message as a QR Code and output results. """
    success = False
    target_file_path = await context.client.download_media(
        await context.get_reply_message()
    )
    if not target_file_path:
        await context.edit(f"{lang('error_prefix')}{lang('parseqr_nofile')}")
        return
    try:
        message = str(decode(Image.open(target_file_path))[0].data)[2:][:-1]
        success = True
        await context.edit(f"**{lang('parseqr_content')}: **\n"
                           f"`{message}`")
    except IndexError:
        await context.edit(f"{lang('error_prefix')}{lang('parseqr_e_noqr')}")
        message = None
    if success:
        await log(f"{lang('parseqr_log')} `{message}`.")
    remove(target_file_path)
