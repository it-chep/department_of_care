import asyncio
import signal
from contextlib import asynccontextmanager
from pyrogram import filters, enums
from pyrogram.errors import ChannelPrivate, RPCError
from pyrogram.types import Message
from app.init import telegram_client
from fastapi import FastAPI
from pyrogram import idle

from app.entities.user import UserToWelcome
from app.repository.new_medblogers_chat_user import Repository

repo = Repository()


async def graceful_shutdown():
    print("🛑 Остановка бота...")
    await telegram_client.client.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Обработка сигналов для graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(graceful_shutdown()))

    pyrogram_task = asyncio.create_task(run_pyrogram_handlers())
    yield
    pyrogram_task.cancel()
    try:
        await pyrogram_task
    except asyncio.CancelledError:
        pass
    await graceful_shutdown()


app = FastAPI(
    title="FastAPI Telegram Group Manager Backend",
    lifespan=lifespan
)


@telegram_client.client.on_message(filters.user([7816396290]))
async def handle_getcource_notification(client, message: Message):
    try:
        if message.text and "Вам пишет" in message.text:
            await telegram_client.client.send_message(
                chat_id=-1001633906217,
                text="@nutrio_agent @readydoc \n\nНа почту пришло новое уведомление. Прошу проверить ГК\n\nP.S. Сообщение "
                     "отправлено автоматически"
            )
    except ChannelPrivate:
        print("❌ Нет доступа к чату -1001633906217")
    except RPCError as e:
        print(f"⚠️ Ошибка Telegram: {e}")


@telegram_client.client.on_message(filters.regex("test_necheporuk"))
async def handle_getcource_notification(client, message: Message):
    print(f"{message.from_user.id}, {message.from_user.first_name} дернулась ручка тестов")
    await telegram_client.client.send_message(
        chat_id=message.chat.id,
        text="привет от бота"
    )


# -1001507744756 - чат вакансий
# -1001711390197 - чат рекламы
@telegram_client.client.on_message(
    filters.chat([-1001507744756, -1001711390197]) & filters.regex(r'has been kicked from the chat because this user is in spam list')
)
async def handle_delete_notification(client, message: Message):
    await message.delete()


@telegram_client.client.on_message(filters.new_chat_members & filters.chat([-1001600505428]))
async def handle_new_chat_member(client, message: Message):
    new_members = message.new_chat_members

    for member in new_members:
        if member.is_bot or repo.check_user_welcome(member.id):
            continue

        repo.create_new_welcome(UserToWelcome(
            tg_id=member.id,
            username=member.username or "",
            first_name=member.first_name
        ))

        name = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
        if message.from_user.username:
            name = f"@{message.from_user.username}"

        await message.reply(
            text=f"{name} ПРИДЭП, юный медблогерец, добро пожаловать на тусовку 😎\n\n"
                 f"Внимательно прочитай все закрепы и напиши в этот чат #знакомство по примеру https://t.me/c/1600505428/70\n\n"
                 f"А затем начинай:\n"
                 f"- изучать базу знаний из 150+ лекций на геткурсе\n"
                 f"- участвовать в наших челленджах\n"
                 f"- общаться с резидентами в этом чате 🩵",
            parse_mode=enums.ParseMode.HTML,
        )

@telegram_client.client.on_message(
    filters.text & filters.chat([-1001600505428]) & filters.regex(r'migrate_users_to_prod'))
async def handle_migrate_members(client, message: Message):
    async for member in message.chat.get_members():
        if not repo.check_user_welcome(member.user.id):
            user_data = UserToWelcome(
                tg_id=member.user.id,
                first_name=member.user.first_name,
                username=member.user.username or "",
            )

            repo.create_new_welcome(user_data)

            print(f"✅ Cохранил {member.user.first_name}")

            await asyncio.sleep(0.5)


async def run_pyrogram_handlers():
    """Запускает обработчики Pyrogram в фоновом режиме"""
    print("🚀 Стартую телеграм юзер бота")
    try:
        await telegram_client.start()
        await idle()
    except Exception as e:
        print(f"🔥 Критическая ошибка: {e}")
    finally:
        await graceful_shutdown()



@app.get("/")
async def root():
    return {"status": "OK"}


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_pyrogram_handlers())
    except KeyboardInterrupt:
        print("🛑 Получен сигнал прерывания")
    finally:
        if loop.is_running():
            loop.close()
        print("👋 Бот завершил работу")
