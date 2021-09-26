from telethon import events, Button
from app.db import *
from app import bot
import random
import string
import os

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
            await bot.send_message(user, msg, buttons=keyboard)


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

    save_user_answer(id, res, event.chat.username)
    print(id, res)
    await event.edit(msg)
    await send_next_task(event)


@bot.on(events.NewMessage(func=lambda e: e.text.lower() == '/download'))
async def on_download_results(event: events.ChatAction.Event):
    results = get_success_results()
    file_prefix = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=7))
    with open(file_prefix + ".ba-ru.txt", "wt") as bf:
        for result in results:
            bf.write(f'{result["date"]}\t{result["ba"].strip()}\t{result["ru"].strip()}\n')

    await bot.send_file(event.chat.username, file_prefix + ".ba-ru.txt")

    os.remove(file_prefix + ".ba-ru.txt")


@bot.on(events.NewMessage(func=lambda e: e.text.lower() == '/stat'))
async def on_download_results(event: events.ChatAction.Event):
    result = get_stat()
    msg = f'<b>Статистика</b>\n' \
          f'Ярҙамсылар һаны: {result.get("author", 0)}\n' \
          f'Һөйләмдәр һаны: {result.get("pairs", 0)}\n' \
          f'Дөрөҫ тип тикшерелгәне: {result.get("success")}\n' \
          f'Хаталы тип тикшерелгәне: {result.get("fail")}\n'
    await bot.send_message(event.chat.username, msg)


@bot.on(events.NewMessage(func=lambda e: '/admin-message' in e.text))
async def on_download_results(event: events.ChatAction.Event):
    if event.chat.username.lower() != SUPER_ADMIN:
        return

    users = get_users()
    result = get_stat()

    admin_msg = event.text.replace('/admin-message ', '')

    msg = f'{admin_msg}\n\n<b>Әлеге ваҡытҡа һөҙөмтә:</b>\n' \
          f'$$$\n' \
          f'Бөтәһе тикшерелгән: {result.get("success") + result.get("fail")}\n' \
          f'Дөрөҫ тип тикшерелгәне: {result.get("success")}\n' \
          f'Хаталы тип тикшерелгәне: {result.get("fail")}\n' \
          f'Ярҙамсылар һаны: {result.get("author", 0)}\n' \
          f'Һөйләмдәр һаны: {result.get("pairs", 0)}\n'

    for r in users:
        if r is not None:
            user_stat = get_user_stat(r)
            user_msg = msg.replace("$$$", f"Һин тикшергәне: {user_stat}")
            keyboard = [
                [
                    Button.inline("Дауам итергә", f'-1 -1'),
                ]
            ]
            await bot.send_message(r, user_msg, buttons=keyboard)
