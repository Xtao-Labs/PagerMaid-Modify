""" PagerMaid features that uses external HTTP APIs other than Telegram. """

from googletrans import Translator, LANGUAGES
from os import remove
from magic_google import MagicGoogle
from gtts import gTTS
from re import compile as regex_compile
from pagermaid import log
from pagermaid.listener import listener, config
from pagermaid.utils import clear_emojis, attach_log, fetch_youtube_audio


@listener(is_plugin=False, outgoing=True, command="translate",
          description="通过 Google 翻译将目标消息翻译成指定的语言。（支持回复）",
          parameters="<文本>")
async def translate(context):
    """ PagerMaid universal translator. """
    translator = Translator()
    reply = await context.get_reply_message()
    message = context.arguments
    lang = config['application_language']
    if message:
        pass
    elif reply:
        message = reply.text
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    try:
        await context.edit("正在生成翻译中 . . .")
        try:
            result = translator.translate(clear_emojis(message), dest=lang)
        except:
            from translate import Translator as trans
            result = trans(to_lang=lang.replace('zh-cn', 'cn').translate(clear_emojis(message))
    except ValueError:
        await context.edit("出错了呜呜呜 ~ 找不到目标语言，请更正配置文件中的错误。")
        return

    source_lang = LANGUAGES[f'{result.src.lower()}']
    trans_lang = LANGUAGES[f'{result.dest.lower()}']
    result = f"**文本翻译** 源语言 {source_lang.title()}:\n{result.text}"

    if len(result) > 4096:
        await context.edit("输出超出 TG 限制，正在尝试上传文件。")
        await attach_log(result, context.chat_id, "translation.txt", context.id)
        return
    await context.edit(result)
    if len(result) <= 4096:
        await log(f"把 `{message}` 从 {source_lang} 翻译到了 {trans_lang}")
    else:
        await log(f"把一条消息从 {source_lang} 翻译到了 {trans_lang}.")


@listener(is_plugin=False, outgoing=True, command="tts",
          description="通过 Google文本到语音 基于字符串生成语音消息。",
          parameters="<string>")
async def tts(context):
    """ Send TTS stuff as voice message. """
    reply = await context.get_reply_message()
    message = context.arguments
    lang = config['application_tts']
    if message:
        pass
    elif reply:
        message = reply.text
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    try:
        await context.edit("生成语音中 . . .")
        gTTS(message, lang=lang)
    except AssertionError:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    except ValueError:
        await context.edit('出错了呜呜呜 ~ 找不到目标语言，请更正配置文件中的错误。')
        return
    except RuntimeError:
        await context.edit('出错了呜呜呜 ~ 加载语言数组时出错。')
        return
    google_tts = gTTS(message, lang=lang)
    google_tts.save("vocals.mp3")
    with open("vocals.mp3", "rb") as audio:
        line_list = list(audio)
        line_count = len(line_list)
    if line_count == 1:
        google_tts = gTTS(message, lang=lang)
        google_tts.save("vocals.mp3")
    with open("vocals.mp3", "r"):
        await context.client.send_file(context.chat_id, "vocals.mp3", voice_note=True)
        remove("vocals.mp3")
        if len(message) <= 4096:
            await log(f"生成了一条文本到语音的音频消息 ： `{message}`.")
        else:
            await log("生成了一条文本到语音的音频消息。")
        await context.delete()


@listener(is_plugin=False, outgoing=True, command="google",
          description="使用 Google 查询",
          parameters="<query>")
async def googletest(context):
    """ Searches Google for a string. """
    mg = MagicGoogle()
    reply = await context.get_reply_message()
    query = context.arguments
    if query:
        pass
    elif reply:
        query = reply.text
    else:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return

    query = query.replace(' ', '+')
    await context.edit("正在拉取结果 . . .")
    results = ""
    for i in mg.search(query=query, num=int(config['result_length'])):
        try:
            title = i['text'][0:30] + '...'
            link = i['url']
            results += f"\n[{title}]({link}) \n"
        except:
            await context.edit("连接到 google服务器 失败")
            return
    await context.edit(f"**Google** |`{query}`| 🎙 🔍 \n"
                       f"{results}",
                       link_preview=False)
    await log(f"在Google搜索引擎上查询了 `{query}`")


@listener(is_plugin=False, outgoing=True, command="fetchaudio",
          description="从多个平台获取音频文件。",
          parameters="<url>,<string>")
async def fetchaudio(context):
    if context.arguments:
        if ',' in context.arguments:
            url, string_2 = context.arguments.split(',', 1)
        else:
            url = context.arguments
            string_2 = "#audio "
    else:
        await context.edit("出错了呜呜呜 ~ 错误的语法。")
        return
    """ Fetches audio from provided URL. """
    reply = await context.get_reply_message()
    reply_id = None
    await context.edit("拉取音频中 . . .")
    if reply:
        reply_id = reply.id
    if url is None:
        await context.edit("出错了呜呜呜 ~ 无效的参数。")
        return
    youtube_pattern = regex_compile(r"^(http(s)?://)?((w){3}.)?youtu(be|.be)?(\.com)?/.+")
    if youtube_pattern.match(url):
        if not await fetch_youtube_audio(url, context.chat_id, reply_id, string_2):
            await context.edit("出错了呜呜呜 ~ 原声带下载失败。")
        await log(f"从链接中获取了一条音频，链接： {url}.")
        await context.delete()
