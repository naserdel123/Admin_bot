# -*- coding: utf-8 -*-

import logging
import os
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.getenv("TOKEN")  # توكن البوت من Render

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# رسالة البداية
PRIVATE_START = """
أهلاً بك 👋

أضفني إلى مجموعتك واجعلني مشرفاً.

الأوامر:
/kick
/ban
/unban
/mute
/unmute
/promote
/demote
/admins
/id

للبحث عن أغنية:
اكتب:
بحث اسم الأغنية

المطور: @N_Naser11
"""

GROUP_START = "أنا بوت إدارة مجموعات 🤖"

# دوال مساعدة
async def is_admin(update, context):
    member = await update.effective_chat.get_member(update.effective_user.id)
    return member.status in ["administrator", "creator"]

async def bot_is_admin(update, context):
    member = await update.effective_chat.get_member(context.bot.id)
    return member.status in ["administrator", "creator"]

def get_target(update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    return None

# أوامر عامة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text(PRIVATE_START)
    else:
        await update.message.reply_text(GROUP_START)

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        await update.message.reply_text(
            f"ID المستخدم: {update.message.reply_to_message.from_user.id}"
        )
    else:
        await update.message.reply_text(f"ID الخاص بك: {update.effective_user.id}")

# أوامر الإدارة
async def kick(update, context):
    if not await is_admin(update, context):
        await update.message.reply_text("Admins only")
        return
    if not await bot_is_admin(update, context):
        await update.message.reply_text("Bot must be admin")
        return

    user = get_target(update)
    if not user:
        await update.message.reply_text("Reply to user")
        return

    await update.effective_chat.ban_member(user.id)
    await update.effective_chat.unban_member(user.id)
    await update.message.reply_text("User kicked")

async def ban(update, context):
    if not await is_admin(update, context):
        return
    user = get_target(update)
    if not user:
        return
    await update.effective_chat.ban_member(user.id)
    await update.message.reply_text("User banned")

async def unban(update, context):
    if not await is_admin(update, context):
        return
    user = get_target(update)
    if not user:
        return
    await update.effective_chat.unban_member(user.id)
    await update.message.reply_text("User unbanned")

async def mute(update, context):
    if not await is_admin(update, context):
        return
    user = get_target(update)
    if not user:
        return

    permissions = ChatPermissions(can_send_messages=False)
    await update.effective_chat.restrict_member(user.id, permissions)
    await update.message.reply_text("User muted")

async def unmute(update, context):
    if not await is_admin(update, context):
        return
    user = get_target(update)
    if not user:
        return

    permissions = ChatPermissions(can_send_messages=True)
    await update.effective_chat.restrict_member(user.id, permissions)
    await update.message.reply_text("User unmuted")

async def promote(update, context):
    if not await is_admin(update, context):
        return
    user = get_target(update)
    if not user:
        return

    await update.effective_chat.promote_member(
        user.id,
        can_delete_messages=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_invite_users=True,
    )
    await update.message.reply_text("Promoted")

async def demote(update, context):
    if not await is_admin(update, context):
        return
    user = get_target(update)
    if not user:
        return

    await update.effective_chat.promote_member(
        user.id,
        can_delete_messages=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_invite_users=False,
    )
    await update.message.reply_text("Demoted")

async def admins(update, context):
    admins = await update.effective_chat.get_administrators()
    text = "Admins:\n"
    for admin in admins:
        text += f"- {admin.user.full_name}\n"
    await update.message.reply_text(text)

# البحث بدون /
async def search_song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.startswith("بحث"):
        return

    query = text.replace("بحث", "").strip()
    if not query:
        return

    await update.message.reply_text("Searching...")

    os.system(f'yt-dlp -x --audio-format mp3 -o "song.%(ext)s" "ytsearch1:{query}"')

    for file in os.listdir():
        if file.endswith(".mp3"):
            await update.message.reply_audio(audio=open(file, "rb"))
            os.remove(file)
            break

# تشغيل البوت
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("admins", admins))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_song))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()