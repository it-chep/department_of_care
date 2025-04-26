import asyncio
from contextlib import asynccontextmanager
from pyrogram import filters
from pyrogram.types import Message
from app.init import telegram_client
from fastapi import FastAPI
from pyrogram import idle

from app.entities.user import UserToWelcome
from app.repository.new_medblogers_chat_user import Repository

repo = Repository()


@asynccontextmanager
async def lifespan(app: FastAPI):
    pyrogram_task = asyncio.create_task(run_pyrogram_handlers())
    yield
    pyrogram_task.cancel()
    try:
        await pyrogram_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="FastAPI Telegram Group Manager Backend",
    lifespan=lifespan
)


@telegram_client.client.on_message(filters.user([7816396290]))
async def handle_getcource_notification(client, message: Message):
    if message.text and "Вам пишет" in message.text:
        await telegram_client.client.send_message(
            chat_id=-1001633906217,
            text="@nutrio_agent @readydoc \n\nНа почту пришло новое уведомление. Прошу проверить ГК\n\nP.S. Сообщение "
                 "отправлено автоматически"
        )


@telegram_client.client.on_message(filters.regex("test"))
async def handle_getcource_notification(client, message: Message):
    await telegram_client.client.send_message(
        chat_id=message.chat.id,
        text="привет от бота"
    )


# -1001507744756 - чат вакансий
# -1001711390197 - чат рекламы
@telegram_client.client.on_message(
    filters.chat([-1001507744756, -1001711390197]) & filters.regex(r'has been kicked from the chat')
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

        await message.reply(
            f"{member.first_name} ПРИДЭП, юный медблогерец, добро пожаловать на тусовку 😎\n\n"
            f"Внимательно прочитай все закрепы и напиши в этот чат #знакомство по примеру https://t.me/c/1600505428/70\n\n"
            f"А затем начинай:\n"
            f"- изучать базу знаний из 150+ лекций на геткурсе\n"
            f"- участвовать в наших челленджах\n"
            f"- общаться с резидентами в этом чате 🩵"
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
    print(f"Стартую телеграм юзер бота")

    await telegram_client.start()
    await idle()


@app.get("/")
async def root():
    return {"status": "OK"}


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_pyrogram_handlers())
    except KeyboardInterrupt:
        print("Остановка бота...")
        loop.run_until_complete(telegram_client.client.stop())
    finally:
        loop.close()
