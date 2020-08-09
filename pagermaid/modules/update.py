""" Pulls in the new version of PagerMaid from the git server. """

from os import remove
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import execute


@listener(is_plugin=False, outgoing=True, command="update",
          description="从远程来源检查更新，并将其安装到 PagerMaid-Modify。",
          parameters="<boolean>")
async def update(context):
    if len(context.parameter) > 1:
        await context.edit("无效的参数。")
        return
    await context.edit("正在检查远程源以进行更新 . . .")
    parameter = None
    if len(context.parameter) == 1:
        parameter = context.parameter[0]
    repo_url = 'https://github.com/xtaodada/PagerMaid-Modify.git'

    try:
        repo = Repo()
    except NoSuchPathError as exception:
        await context.edit(f"出错了呜呜呜 ~ 目录 {exception} 不存在。")
        return
    except InvalidGitRepositoryError:
        await context.edit(f"此 PagerMaid-Modify 实例不是从源安装,"
                           f" 请通过您的本机软件包管理器进行升级。")
        return
    except GitCommandError as exception:
        await context.edit(f'出错了呜呜呜 ~ 收到了来自 git 的错误: `{exception}`')
        return

    active_branch = repo.active_branch.name
    if not await branch_check(active_branch):
        await context.edit(
            f"出错了呜呜呜 ~ 该分支未维护: {active_branch}.")
        return

    try:
        repo.create_remote('upstream', repo_url)
    except BaseException:
        pass

    upstream_remote = repo.remote('upstream')
    upstream_remote.fetch(active_branch)
    changelog = await changelog_gen(repo, f'HEAD..upstream/{active_branch}')

    if not changelog:
        await context.edit(f"`PagerMaid-Modify 在分支 ` **{active_branch}**` 中已是最新。`")
        return

    if parameter != "true":
        changelog_str = f'**找到分支 {active_branch} 的更新.\n\n更新日志:**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await context.edit("更新日志太长，正在附加文件。")
            file = open("output.log", "w+")
            file.write(changelog_str)
            file.close()
            await context.client.send_file(
                context.chat_id,
                "output.log",
                reply_to=context.id,
            )
            remove("output.log")
        else:
            await context.edit(changelog_str + "\n**执行 \"-update true\" 来安装更新。**")
        return

    await context.edit('找到更新，正在拉取 . . .')

    try:
        try:
            upstream_remote.pull(active_branch)
        except:
            await execute("""git status | grep modified | sed -r "s/ +/ /" | cut -f2 | awk -F " " '{print "mkdir -p $(dirname ../for-update/" $2 ") && mv " $2 " ../for-update/" $2}' | sh""")
            await execute("git pull")
            await execute("""cd ../for-update/ && find -H . -type f | awk '{print "cp " $1 " ../PagerMaid-Modify/" $1}' | sh && cd ../PagerMaid-Modify""")
            await execute("rm -rf ../for-update/")
        await execute("python3 -m pip install -r requirements.txt --upgrade")
        await execute("python3 -m pip install -r requirements.txt")
        await log("PagerMaid-Modify 已更新。")
        await context.edit(
            '更新成功，PagerMaid-Modify 正在重新启动。'
        )
        await context.client.disconnect()
    except GitCommandError:
        upstream_remote.git.reset('--hard')
        await log("PagerMaid-Modify 更新失败。")
        await context.edit(
            '更新时出现错误，PagerMaid-Modify 正在重新启动。'
        )
        await context.client.disconnect()


async def changelog_gen(repo, diff):
    result = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        result += f'•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n'
    return result


async def branch_check(branch):
    official = ['master', 'staging']
    for k in official:
        if k == branch:
            return 1
    return
