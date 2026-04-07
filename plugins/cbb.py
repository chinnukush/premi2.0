
from pyrogram import Client 
from bot import Bot
from config import *
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.database import *

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
            ])
        )

    elif data == "about":
        await query.message.edit_text(
            text=ABOUT_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton('ᴄʟᴏꜱᴇ', callback_data='close')]
            ])
        )

    elif data == "start":
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(' 📢 ɪᴏɪɴ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ', url='https://t.me/hari_moviez')
             ],
                [InlineKeyboardButton('🔍 ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ ɢʀᴏᴜᴘ 𝟷', url='https://t.me/iPopcornMoviesGroups'),
                 InlineKeyboardButton('🧭 ᴍᴏᴠɪᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/+WQbEWONPmgA3ZDA1')]]))

    elif data == "premium":
        await query.message.delete()
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=QR_PIC,
            caption=(
                f"<b>👋 ʜᴇʏ ʜɪɪ {query.from_user.username}\n\n</b>"
                f"🎖️ ʜᴇʀᴇ ɪꜱ ꜱᴏᴍᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴꜱ :\n\n"
                f"● {PRICE1}  ғᴏʀ 𝟶𝟽 ᴅᴀʏꜱ ᴘʀɪᴍᴇ ᴍᴇᴍʙᴇʀꜱʜɪᴘ\n\n"
                f"● {PRICE2}  ғᴏʀ 𝟶𝟷 ᴍᴏɴᴛʜ ᴘʀɪᴍᴇ ᴍᴇᴍʙᴇʀꜱʜɪᴘ\n\n"
                f"● {PRICE3}  ғᴏʀ 𝟶𝟹 ᴍᴏɴᴛʜꜱ ᴘʀɪᴍᴇ ᴍᴇᴍʙᴇʀꜱʜɪᴘ\n\n"
                f"● {PRICE4}  ғᴏʀ 𝟶𝟼 ᴍᴏɴᴛʜꜱ ᴘʀɪᴍᴇ ᴍᴇᴍʙᴇʀꜱʜɪᴘ\n\n"
                f"● {PRICE5}  ғᴏʀ 𝟶𝟷 ʏᴇᴀʀ ᴘʀɪᴍᴇ ᴍᴇᴍʙᴇʀꜱʜɪᴘ\n\n\n"
                f"💵 ᴜᴘɪ ɪᴅ ᴛᴏ ᴘᴀʏ -  <code>{UPI_ID}</code>\n\n\n"
                f"♻️ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ɪɴꜱᴛᴀɴᴛ ᴍᴇᴍʙᴇʀꜱʜɪᴘ \n\n\n"
                f"‼️ ᴍᴜꜱᴛ ꜱᴇɴᴅ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ & Iғ ᴀɴʏᴏɴᴇ ᴡᴀɴᴛ ᴄᴜꜱᴛᴏᴍ ᴛɪᴍᴇ ᴍᴇᴍʙʀꜱʜɪᴘ ᴛʜᴇɴ ᴀꜱᴋ ᴀᴅᴍɪɴ"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "ADMIN 24/7", url=(SCREENSHOT_URL)
                        )
                    ],
                    [InlineKeyboardButton("🔒 Close", callback_data="close")],
                ]
            )
        )



    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await db.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "ᴏғғ" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        cid, action = data.split("_")[2:]
        cid = int(cid)
        mode = "on" if action == "on" else "off"

        await db.set_channel_mode(cid, mode)
        await query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        # Refresh the same channel's mode view
        chat = await client.get_chat(cid)
        status = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await query.message.edit_text(
            f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "fsub_back":
        channels = await db.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await db.get_channel_mode(cid)
                status = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except:
                continue

        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
