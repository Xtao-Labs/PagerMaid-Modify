""" Pulls in the new version of PagerMaid from the git server. """

import platform
from subprocess import run, PIPE
from datetime import datetime
from time import strftime
from os import remove
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import execute, lang


@listener(is_plugin=False, outgoing=True, command="update",
          description=lang('update_des'),
          parameters="<true/debug>")
async def update(context):
    if len(context.parameter) > 1:
        await context.edit(lang('arg_error'))
        return
    await context.edit(lang('update_processing'))
    parameter = None
    if len(context.parameter) == 1:
        parameter = context.parameter[0]
    repo_url = 'https://github.com/xtaodada/PagerMaid-Modify.git'

    if parameter:
        if parameter == "debug":
            # Version info
            git_version = run("git --version", stdout=PIPE, shell=True).stdout.decode().strip().replace("git version ", "")
            git_change = bool(run("git diff-index HEAD --", stdout=PIPE, shell=True).stdout.decode().strip())
            git_change = "是" if git_change else "否"
            git_date = run("git log -1 --format='%at'", stdout=PIPE, shell=True).stdout.decode()
            git_date = datetime.utcfromtimestamp(int(git_date)).strftime("%Y/%m/%d %H:%M:%S")
            git_hash = run("git rev-parse --short HEAD", stdout=PIPE, shell=True).stdout.decode().strip()
            get_hash_link = f"https://github.com/xtaodada/PagerMaid-Modify/commit/{git_hash}"
            # Generate the text
            text = f"{lang('status_platform')}: {str(platform.platform())}\n{lang('update_platform_version')}: {str(platform.version())}\n {lang('status_python')}: {str(platform.python_version())}\n {lang('update_git_version')}: {git_version}\n {lang('update_local_git_change')}: {git_change}\n {lang('update_hash')}: [{git_hash}]({get_hash_link})\n {lang('update_date')}: {git_date} "
            await context.edit(text)
            return

    try:
        repo = Repo()
    except NoSuchPathError as exception:
        await context.edit(f"{lang('update_NoSuchPathError')} {exception}")
        return
    except InvalidGitRepositoryError:
        await context.edit(lang('update_InvalidGitRepositoryError'))
        return
    except GitCommandError as exception:
        await context.edit(f'{lang("update_GitCommandError")} :`{exception}`')
        return

    active_branch = repo.active_branch.name
    if not await branch_check(active_branch):
        await context.edit(
            f"{lang('update_not_active_branch')}: {active_branch}.")
        return

    try:
        repo.create_remote('upstream', repo_url)
    except BaseException:
        pass

    upstream_remote = repo.remote('upstream')
    upstream_remote.fetch(active_branch)
    changelog = await changelog_gen(repo, f'HEAD..upstream/{active_branch}')


    if not parameter:
        if not changelog:
            await context.edit(f"`PagerMaid-Modify {lang('update_in_branch')} ` **{active_branch}**` {lang('update_is_updated')}`")
            return
        changelog_str = f'**{lang("update_found_update_in_branch")} {active_branch}.\n\n{lang("update_change_log")}:**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await context.edit(lang('update_log_too_big'))
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
            await context.edit(changelog_str + f"\n**{lang('update_hint')}**\n`-update true`")
        return


    await context.edit(lang('update_found_pulling'))

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
        await log(f"PagerMaid-Modify {lang('update_is_updated')}")
        await context.edit(lang('update_success') + lang('apt_reboot'))
        await context.client.disconnect()
    except GitCommandError:
        upstream_remote.git.reset('--hard')
        await log(lang('update_failed'))
        await context.edit(lang('update_failed') + lang('apt_reboot'))
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
