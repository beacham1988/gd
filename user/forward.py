#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import random
import os
import re
import sys
import json
import time
import requests
from telethon import events
from .login import user
from .. import chat_id, jdbot, logger, TOKEN
from ..bot.utils import cmd, V4
from ..diy.utils import rwcon, myzdjr_chatIds, my_chat_id, jk

jk_version = 'v1.2.9'
from ..bot.update import version as jk_version
from cacheout import FIFOCache


def now():
    return int(time.time())


# 缓存先进先出
cache = FIFOCache(maxsize=512, ttl=0)
queue = FIFOCache(maxsize=128, ttl=0)

bot_id = int(TOKEN.split(":")[0])
client = user
# 转发群
forward_chatId = -1001545202667
# wuxian机器人ID
wuxian_BotId = 2045692757
# 最后一次wuxian时间
last_exec_time = now() - 60


async def check_next_activity(done=False):
    if queue.size() > 0:
        if done or now() - last_exec_time >= 60:
            next_activity_tuple = queue.popitem()
            await done_new_activity(next_activity_tuple[0])


async def done_new_activity(activity_id):
    global last_exec_time
    last_exec_time = now()
    await user.send_message(wuxian_BotId, f"wuxian {activity_id}")


async def add_new_activity(activity_id):
    queue.add(activity_id, activity_id)
    await check_next_activity()


@client.on(events.NewMessage(chats=[wuxian_BotId]))
async def wuxian_msg(event):
    if re.search(r"消息提醒: 京东超级互动城", event.message.text, re.M):
        await check_next_activity(True)
    else:
        await check_next_activity()


# @client.on(events.NewMessage(pattern=r"[\s\S]*([\da-z]{32})[\s\S]*"))
@client.on(events.NewMessage())
async def jiexi_activity(event):
    try:
        await check_next_activity()
        if event.chat_id == wuxian_BotId:
            return
        id_match = re.search(r"(([\da-z]{32}\|)*[\da-z]{32})", event.message.text, re.M)
        if id_match:
            msg = "监听到无线活动ID"
            activity_id = id_match.group(1)
            if cache.has(activity_id):
                msg += "，旧的，跳过"
            else:
                msg += "，新的，开跑"
                cache.add(activity_id, activity_id, ttl=10800)
                await add_new_activity(activity_id)
            if event.chat_id != forward_chatId:
                forward_message = await user.forward_messages(forward_chatId, event.id, event.chat_id)
                await forward_message.reply(msg)
            else:
                await event.message.reply(msg)
    except Exception as e:
        logger.error(str(e))



