from telethon import events, Button
from telethon.errors import UserIsBlockedError
from telethon.tl.types import InputPeerUser

from app.db import *
from app import bot
import random
import string
import os

from app.session import get_bot_users
from config import SUPER_ADMIN


def generate_option(task):
    msg = f'<b>Башҡортса</b>\n' \
          f'{task["ba"]}\n' \
          f'<b>Русса</b>\n' \
          f'{task["ru"]}\n' \
          f'<b>Мәғәнәһе дөрөҫ тәржемә ителгәнме?</b>'

    return msg, task["id"]


@bot.on(events.NewMessage(func=lambda e: e.text.lower() == '/start'))
async def on_start(event: events.ChatAction.Event):
    hi_msg = f'Сәләм, <b>{event.chat.first_name} {event.chat.last_name}</b>.\n' \
             f'Был чат башҡорт-рус параллель корпусының күләмен арттырыу өсөн эшләнгән. ' \
             f'Аҙаҡ был эштәр  ru.glosbe.com/ru/ba, bashkortsoft.ru һәм башҡа машина ярҙамында тәржемә итеү сайттарында ҡулланыласаҡ.\n\n' \
             f'<b>Нисек һин беҙгә ярҙам итә алаң?</b>\n' \
             f'Әйтәйек, беҙҙә бер әҫәр ике телдә бар. ' \
             f'Иң тәүҙә беҙ автоматик рәүештә һәр башҡорт һөйләменең рус вариантында булған тәржемәһен табабыҙ. ' \
             f'Әммә был ғына корпус төҙөүгә етмәй. Беҙгә кешенең ҡарап сығыуы кәрәк. \n\n' \
             f'Һеҙгә ике телдә һөйләм бирелә: башҡортса һәм шул һөйләмдең русса тәржемәһе. ' \
             f'Һеҙ шул тәржемә <b>бөткәнсе мәғәнәне дөрөҫ еткерәме</b>, шуны әйтергә тейешһегеҙ. \n' \
             f'Башланыҡ!'

    await event.respond(hi_msg)
    await send_next_task(event)


async def send_next_task(event: events.ChatAction.Event, user=None):
    task = get_next_task()
    if task is not None:
        msg, id = generate_option(task)
        keyboard = [
            [
                Button.inline("👎", f'{id} 0'),
                Button.inline("👍", f'{id} 1'),
            ]
        ]

        if user is None:
            await event.respond(msg, buttons=keyboard)
        else:
            try:
                await bot.send_message(user, msg, buttons=keyboard)
            except UserIsBlockedError:
                # add_blocked_user(user)
                return False
        return True


@bot.on(events.CallbackQuery)
async def callback(event):
    id, res = event.data.decode("utf-8").split(' ')

    if id == "-1":
        await send_next_task(event)
        return

    task = get_raw_pair(id)
    msg = f'<b>Башҡортса</b>\n' \
          f'{task["ba"]}\n' \
          f'<b>Русса</b>\n' \
          f'{task["ru"]}\n' \
          f'Һеҙ {"👍" if res == "1" else "👎"} тип яуап бирҙегеҙ. Рәхмәт! Киләһе эш:'

    save_user_answer(id, res, event.chat.username, event.chat_id)
    print(id, res)
    await event.edit(msg)
    await send_next_task(event)


@bot.on(events.NewMessage(func=lambda e: e.text.lower() == '/download'))
async def on_download_results(event: events.ChatAction.Event):
    results = get_success_results()
    file_prefix = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=7))
    with open(file_prefix + ".ba-ru.tsv", "wt") as bf:
        bf.write(
            f'Дата\tБашҡортса\tРусса\n')

        for result in results:
            bf.write(
                f'{result["date"]}\t{result["ba"].strip()}\t{result["ru"].strip()}\n')

    await bot.send_file(event.chat.username, file_prefix + ".ba-ru.tsv")

    os.remove(file_prefix + ".ba-ru.tsv")


@bot.on(events.NewMessage(func=lambda e: e.text.lower() == '/stat'))
async def on_download_results(event: events.ChatAction.Event):
    result = get_stat()
    users = get_bot_users()

    msg = f'<b>Статистика</b>\n' \
          f'Ярҙамсылар һаны: {len(users)}\n' \
          f'Һөйләмдәр һаны: {result.get("pairs", 0)}\n' \
          f'Дөрөҫ тип тикшерелгәне: {result.get("success")}\n' \
          f'Хаталы тип тикшерелгәне: {result.get("fail")}\n'
    await bot.send_message(event.chat.username, msg)


@bot.on(events.NewMessage(func=lambda e: '/all-stats' in e.text))
async def send_stats_for_all(event: events.ChatAction.Event):
    if event.chat.username.lower() != SUPER_ADMIN:
        return

    users = get_bot_users()
    result = get_stat()

    admin_msg = event.text.replace('/all-stats ', '')

    msg = f'{admin_msg}\n\n<b>Әлеге ваҡытҡа һөҙөмтә:</b>\n' \
          f'Бөтәһе тикшерелгән: {result.get("success") + result.get("fail")}\n' \
          f'Дөрөҫ тип тикшерелгәне: {result.get("success")}\n' \
          f'Хаталы тип тикшерелгәне: {result.get("fail")}\n' \
          f'Ярҙамсылар һаны: {len(users)}\n' \
          f'Һөйләмдәр һаны: {result.get("pairs", 0)}\n'

    for r in users:
        # user_stat = get_user_stat(r)
        # user_msg = msg.replace("$$$", f"Һин тикшергәне: {user_stat}")
        keyboard = [
            [
                Button.inline("Дауам итергә", f'-1 -1'),
            ]
        ]
        user = InputPeerUser(r['id'], r['hash'])
        try:
            await bot.send_message(user, msg, buttons=keyboard)
        except UserIsBlockedError:
            pass
            # add_blocked_user(r)


@bot.on(events.NewMessage(func=lambda e: '/spam2all' in e.text))
async def admin_send_messages_to_all(event: events.ChatAction.Event):
    if event.chat.username.lower() != SUPER_ADMIN:
        return

    users = get_bot_users()

    sended_users = []
    new_blocked_users = []
    for r in users:
        user = InputPeerUser(r['id'], r['hash'])
        send_success = await send_next_task(None, user)
        if send_success:
            sended_users.append(r['name'])
        else:
            new_blocked_users.append(r['name'])

    await bot.send_message(event.chat.username,
                           f"Ошоларға хат ебәрелде: ({len(sended_users)}),\nә былары блокировать итте: {new_blocked_users}({len(new_blocked_users)})")


@bot.on(events.NewMessage(func=lambda e: '/test' in e.text))
async def admin_send_all_stats(event: events.ChatAction.Event):
    if event.chat.username.lower() != SUPER_ADMIN:
        return

    users = get_bot_users()

    await bot.send_message(event.chat.username, f'users: {len(users)}')
