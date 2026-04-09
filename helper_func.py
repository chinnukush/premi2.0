import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import *
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait
from shortzy import Shortzy
from database.database import db


# ================= ADMIN CHECK =================
async def check_admin(filter, client, update):
    try:
        user_id = update.from_user.id
        return user_id == OWNER_ID or await db.admin_exist(user_id)
    except Exception as e:
        print(f"[ERROR] check_admin: {e}")
        return False


# ================= FORCE SUB CHECK =================
async def is_subscribed(client, user_id):
    try:
        channel_ids = await db.show_channels()

        if not channel_ids or user_id == OWNER_ID:
            return True

        for cid in channel_ids:
            if not await is_sub(client, user_id, cid):
                mode = await db.get_channel_mode(cid)

                if mode == "on":
                    await asyncio.sleep(2)
                    if await is_sub(client, user_id, cid):
                        continue

                return False

        return True

    except Exception as e:
        print(f"[ERROR] is_subscribed: {e}")
        return False


# ================= SINGLE CHANNEL CHECK =================
async def is_sub(client, user_id, channel_id):
    try:
        member = await client.get_chat_member(channel_id, user_id)

        return member.status in {
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER
        }

    except UserNotParticipant:
        try:
            mode = await db.get_channel_mode(channel_id)

            if mode == "on":
                return await db.req_user_exist(channel_id, user_id)

            return False

        except Exception as e:
            print(f"[ERROR] is_sub (UserNotParticipant): {e}")
            return False

    except Exception as e:
        print(f"[ERROR] is_sub: {e}")
        return False


# ================= ENCODE / DECODE =================
async def encode(string: str):
    try:
        return base64.urlsafe_b64encode(string.encode()).decode().strip("=")
    except Exception as e:
        print(f"[ERROR] encode: {e}")
        return None


async def decode(base64_string: str):
    try:
        base64_string += "=" * (-len(base64_string) % 4)
        return base64.urlsafe_b64decode(base64_string.encode()).decode()
    except Exception as e:
        print(f"[ERROR] decode: {e}")
        return None


# ================= GET MESSAGES =================
async def get_messages(client, message_ids):
    messages = []

    for i in range(0, len(message_ids), 200):
        batch = message_ids[i:i + 200]

        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=batch
            )
            messages.extend(msgs)

        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=batch
            )
            messages.extend(msgs)

        except Exception as e:
            print(f"[ERROR] get_messages: {e}")

    return messages


# ================= FIXED MESSAGE ID (NO WARNINGS) =================
async def get_message_id(client, message):
    try:
        # New Pyrogram method (NO deprecated warnings)
        if message.forward_origin:
            origin = message.forward_origin

            if hasattr(origin, "chat") and origin.chat:
                if origin.chat.id == client.db_channel.id:
                    return getattr(origin, "message_id", 0)

            return 0

        elif message.text:
            pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
            match = re.match(pattern, message.text)

            if not match:
                return 0

            channel_id = match.group(1)
            msg_id = int(match.group(2))

            if channel_id.isdigit():
                if f"-100{channel_id}" == str(client.db_channel.id):
                    return msg_id
            else:
                if channel_id == client.db_channel.username:
                    return msg_id

        return 0

    except Exception as e:
        print(f"[ERROR] get_message_id: {e}")
        return 0


# ================= TIME FORMAT =================
def get_readable_time(seconds: int) -> str:
    try:
        periods = [
            ('days', 86400),
            ('h', 3600),
            ('m', 60),
            ('s', 1)
        ]

        result = []

        for name, count in periods:
            value = seconds // count
            if value:
                seconds %= count
                result.append(f"{value}{name}")

        return " ".join(result) if result else "0s"

    except Exception as e:
        print(f"[ERROR] get_readable_time: {e}")
        return "0s"


def get_exp_time(seconds):
    try:
        periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
        result = ''

        for name, count in periods:
            value = seconds // count
            if value:
                seconds %= count
                result += f"{value} {name} "

        return result.strip()

    except Exception as e:
        print(f"[ERROR] get_exp_time: {e}")
        return ""


# ================= SHORTLINK =================
async def get_shortlink(url, api, link):
    try:
        if not url or not api:
            return link  # skip if not configured

        shortzy = Shortzy(api_key=api, base_site=url)
        return await shortzy.convert(link)

    except Exception as e:
        print(f"[ERROR] shortlink: {e}")
        return link


# ================= FILTERS =================
subscribed = filters.create(is_subscribed)
admin = filters.create(check_admin)
