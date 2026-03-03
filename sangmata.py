import asyncio
import random
import config


from core import app, userbot
from pyrogram import filters, raw
from utils.query_group import sangmata_group
from utils.database import dB
from utils.decorators import ONLY_ADMIN, ONLY_GROUP


@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=sangmata_group,
)
async def sang_mata(client, message):
    if message.sender_chat:
        return

    user_id = message.from_user.id
    first = message.from_user.first_name
    last = message.from_user.last_name
    username = message.from_user.username

    if not await dB.cek_userdata(user_id):
        await dB.add_userdata(user_id, first, last, username)
        return

    data = await dB.get_userdata(user_id)
    if not data:
        return

    old_first = data["depan"]
    old_last = data["belakang"]
    old_username = data["username"]

    changes = []
    if await dB.get_var(message.chat.id, "SICEPU"):
        return

    if old_username != username:
        old_u = f"@{old_username}" if old_username else "<b>Without Username</b>"
        new_u = f"@{username}" if username else "<b>Without Username</b>"
        changes.append(f"<emoji id=5271604874419647061>🔗</emoji><b> Changing the username from <code>{old_u}</code> to <code>{new_u}</code></b>.")

    if old_first != first:
        changes.append(f"<b><emoji id=5271604874419647061>🔗</emoji> Changing the first name from <code>{old_first}</code> to <code>{first}</code>.</b>")

    if old_last != last:
        old_l = old_last or "<b>Without a last name</b>"
        new_l = last or "<b>Without a last name</b>"
        changes.append(f"<b><emoji id=5271604874419647061>🔗</emoji> Changing the last name from <code>{old_l}</code> to <code>{new_l}</code>.</b>")

    if changes:
        msg = f"<emoji id=5372981976804366741>🤖</emoji><b> {client.me.mention} Sang Mata Detected!</b>\n\n"
        msg += f"<b>User : {message.from_user.mention} [<code>{user_id}</code>]</b>\n"
        msg += "\n".join(changes)
        await message.reply_text(f"<blockquote expandable>{msg}</blockquote>", quote=True)

        await dB.add_userdata(user_id, first, last, username)



@app.on_message(filters.command("sangmata") & ~filters.bot & ~filters.via_bot)
@ONLY_ADMIN
@ONLY_GROUP
async def sangmata_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("<emoji id=5210952531676504517>❌</emoji><b>Use format\n<code>/sangmata on</code> to activate SangMata.\n<code>/sangmata off</code> to disable SangMata.</b>")
    state = message.command[1].lower()
    if state not in ["on", "off"]:
        return await message.reply_text("<emoji id=5210952531676504517>❌</emoji><b>Use format\n<code>/sangmata on</code> to activate SangMata.\n<code>/sangmata off</code> to disable SangMata.</b>")
    if state == "on":
        if not await dB.get_var(message.chat.id, "SICEPU"):
            return await message.reply_text("<emoji id=5206607081334906820>✅</emoji>**Sangmata has been activated.**")
        await dB.remove_var(message.chat.id, "SICEPU")
        return await message.reply_text("<emoji id=5206607081334906820>✅</emoji>**Successfully activate Sangmata.**")
    else:
        if await dB.get_var(message.chat.id, "SICEPU"):
            return await message.reply_text("<emoji id=5206607081334906820>✅</emoji>**Sangmata has been turned off**")
        await dB.set_var(message.chat.id, "SICEPU", True)
        return await message.reply_text("<emoji id=5206607081334906820>✅</emoji>**Successfully turned off Sangmata.**")


@app.on_message(filters.command(["sg"]) & ~config.BANNED_USERS)
async def history(client, message):
    reply = message.reply_to_message
    try:
        target = reply.from_user.id if reply else message.text.split()[1]
    except (AttributeError, IndexError):
        return await message.reply("<emoji id=5240241223632954241>🚫</emoji>**Balas pesan pengguna atau berikan username pengguna.**")
    try:
        user_id = (await client.get_users(target)).id
    except Exception:
        user_id = int(message.command[1])
    proses = await message.reply("<emoji id=5386367538735104399>⌛</emoji>**Please wait...**")
    bot = ["@Sangmata_bot", "@SangMata_beta_bot"]
    babu = userbot.clients[0]
    getbot = random.choice(bot)
    await babu.unblock_user(getbot)
    txt = await babu.send_message(getbot, user_id)
    await asyncio.sleep(4)
    await txt.delete()
    await proses.delete()
    async for name in babu.search_messages(getbot, limit=2):
        if not name.text:
            await message.reply(f"<emoji id=5210952531676504517>❌</emoji><b> {getbot} ERROR, Silahkan kirim manual id pengguna ke {''.join(bot)}!</b>")
        else:
            await message.reply(name.text)
    user_info = await babu.resolve_peer(getbot)
    return await babu.invoke(raw.functions.messages.DeleteHistory(peer=user_info, max_id=0, revoke=True))


__MODULE__ = "SangMata"
__HELP__ = """
<blockquote expandable>
<b>🕵️‍♂️ SangMata Tracker</b>

<b>★ /sangmata</b> [on/off] – Enable or disable name change tracking in the group.  
<b>★ /sg</b> [userID/reply] – View user name history.
</blockquote>
"""






