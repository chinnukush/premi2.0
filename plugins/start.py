import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import *
from helper_func import *
from database.database import *
from database.db_premium import *


# ================= SAFE PHOTO ================= #

async def safe_send_photo(message, photo, caption, reply_markup=None):
    try:
        return await message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup
        )
    except Exception as e:
        print("Photo Error:", e)
        return await message.reply_text(
            caption,
            reply_markup=reply_markup
        )


# ================= SHORT LINK ================= #

async def short_url(client: Client, message, base64_string):
    try:
        prem_link = f"https://t.me/{client.username}?start=yu3elk{base64_string}7"
        short_link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, prem_link)

        buttons = [
            [
                InlineKeyboardButton("Download", url=short_link),
                InlineKeyboardButton("Tutorial", url=TUT_VID)
            ],
            [InlineKeyboardButton("Premium", callback_data="premium")]
        ]

        await safe_send_photo(
            message,
            SHORTENER_PIC,
            SHORT_MSG,
            InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        print("Shortlink Error:", e)


# ================= START ================= #

@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message):

    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)

    # Add user
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Force Sub
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # Ban check
    if user_id in await db.get_ban_users():
        return await message.reply_text(
            "⛔️ You are banned.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Support", url=BAN_SUPPORT)]]
            )
        )

    FILE_AUTO_DELETE = await db.get_del_timer()
    text = message.text

    # ================= PAYLOAD ================= #

    if len(text) > 7:
    try:
        data = text.split(" ", 1)[1]

        # Extract base64
        base64_string = data[6:-1] if data.startswith("yu3elk") else data

    except Exception as e:
        print("Payload Error:", e)
        return await message.reply("Invalid link ❌")

    # Decode
    try:
        decoded = await decode(base64_string)
        args = decoded.split("-")
    except Exception as e:
        print("Decode Error:", e)
        return await message.reply("Invalid link ❌")

    ids = []

        try:
            if len(args) == 3:
                start = int(int(args[1]) / abs(client.db_channel.id))
                end = int(int(args[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1)

            elif len(args) == 2:
                ids = [int(int(args[1]) / abs(client.db_channel.id))]
        except:
            return await message.reply("Error decoding ❌")

        temp = await message.reply("⏳ Please wait...")

        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await temp.delete()
            print("Fetch Error:", e)
            return await message.reply("Error fetching files ❌")

        await temp.delete()

        sent_msgs = []

        for msg in messages:
            if not msg or not msg.media:
                continue

            # ✅ FIX 2: skip invalid messages
            if not (msg.text or msg.caption or msg.photo or msg.video or msg.document or msg.audio):
                continue

            caption = msg.caption.html if msg.caption else ""
            caption += f"\n\n{CUSTOM_CAPTION}" if CUSTOM_CAPTION else ""

            try:
                sent = await msg.copy(
                    chat_id=user_id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    protect_content=PROTECT_CONTENT
                )
                sent_msgs.append(sent)
                await asyncio.sleep(0.3)

            except FloodWait as e:
                await asyncio.sleep(e.x)

            except Exception as e:
                print("Copy Error:", e)
                continue

        # ================= AUTO DELETE ================= #

        if FILE_AUTO_DELETE > 0 and sent_msgs:
            notify = await message.reply(
                f"⚠️ File will delete in {get_exp_time(FILE_AUTO_DELETE)}"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for m in sent_msgs:
                try:
                    await m.delete()
                except:
                    pass

            try:
                reload_url = f"https://t.me/{client.username}?start={message.command[1]}"

                await notify.edit(
                    "✅ File deleted. Click below to get again",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("🔄 Get Again", url=reload_url)]]
                    )
                )
            except:
                pass

        elif not sent_msgs:
            await message.reply("❌ No valid files found.")

    # ================= NORMAL START ================= #

    else:
        await safe_send_photo(
            message,
            START_PIC,
            START_MSG.format(mention=message.from_user.mention),
            InlineKeyboardMarkup(
                [[InlineKeyboardButton("Support", url=BAN_SUPPORT)]]
            )
        )


# ================= FORCE SUB ================= #

chat_data_cache = {}

async def not_joined(client: Client, message):
    temp = await message.reply("Checking subscription...")

    user_id = message.from_user.id
    buttons = []

    try:
        channels = await db.show_channels()

        for chat_id in channels:
            if not await is_sub(client, user_id, chat_id):

                if chat_id in chat_data_cache:
                    data = chat_data_cache[chat_id]
                else:
                    data = await client.get_chat(chat_id)
                    chat_data_cache[chat_id] = data

                name = data.title

                if data.username:
                    link = f"https://t.me/{data.username}"
                else:
                    invite = await client.create_chat_invite_link(chat_id)
                    link = invite.invite_link

                buttons.append([InlineKeyboardButton(name, url=link)])

        buttons.append([
            InlineKeyboardButton(
                "🔄 Try Again",
                url=f"https://t.me/{client.username}?start"
            )
        ])

        await safe_send_photo(
            message,
            FORCE_PIC,
            FORCE_MSG.format(mention=message.from_user.mention),
            InlineKeyboardMarkup(buttons)
        )

        await temp.delete()

    except Exception as e:
        print("ForceSub Error:", e)


# ================= OTHER ================= #

@Bot.on_message(filters.command("myplan") & filters.private)
async def myplan(client, message):
    await message.reply(await check_user_plan(message.from_user.id))


@Bot.on_message(filters.command("count") & filters.private & admin)
async def count_cmd(client, message):
    total = await db.get_total_verify_count()
    await message.reply(f"Total Verified: {total}")


@Bot.on_message(filters.command("commands") & filters.private & admin)
async def commands_cmd(client, message):
    await message.reply(
        CMD_TXT,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Close", callback_data="close")]]
        )
    )
