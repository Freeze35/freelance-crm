import os
import django
import asyncio
import logging

# ────────────────────────────────────────────────
# Initializing Django
# ────────────────────────────────────────────────
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')  # ← Replace 'crm' with the name of your project
django.setup()  # ← this loads the settings and prepares the models

from clients.models import Client
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from asgiref.sync import sync_to_async
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
import re

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class RegisterForm(StatesGroup):
    organization = State()
    inn = State()
    email = State()


@dp.message(F.text == "📝 Регистрация")
async def btn_registration(message: types.Message, state: FSMContext):
    await cmd_registration(message, state)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.button(text="📝 Регистрация")
    builder.adjust(1)  # Full-width button

    await message.answer(
        "Привет! 👋\n"
        "Я бот Freelance CRM. Здесь ты можешь получать счета за проекты автоматически.\n\n"
        "Чтобы зарегистрироваться и привязать этот чат к твоему аккаунту в CRM, "
        "отправь команду:\n"
        "👉 /registration\n\n"
        "Или нажми кнопку регистрации\n"
        "После этого я попрошу ввести данные организации.\n",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@dp.message(Command("registration", "reg"))
async def cmd_registration(message: types.Message, state: FSMContext):
    await message.answer(
        "Отлично, начинаем регистрацию! 📝\n\n"
        "Напиши название организации (или ФИО, если ИП):"
    )
    await state.set_state(RegisterForm.organization)


@dp.message(RegisterForm.organization)
async def process_organization(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer("Название организации не может быть пустым. Попробуй ещё раз:")
        return
    await state.update_data(organization=text)
    await message.answer("Отлично! Теперь ИНН или ОГРН:")
    await state.set_state(RegisterForm.inn)


@dp.message(RegisterForm.inn)
async def process_inn(message: types.Message, state: FSMContext):
    inn = message.text.strip()

    # Check: only numbers and length 10 or 12 characters
    if not inn.isdigit() or len(inn) not in [10, 12]:
        await message.answer(
            "⚠️ Некорректный ИНН.\n"
            "ИНН должен состоять только из цифр и иметь длину 10 (для организаций) или 12 (для ИП) символов.\n"
            "Попробуйте ещё раз:"
        )
        return

    await state.update_data(inn=inn)
    await message.answer(
        "Последний шаг — email (для копий счетов).\n\n"
        "Если не нужно — напишите «пропустить»."
    )
    await state.set_state(RegisterForm.email)

@dp.message(RegisterForm.email)
async def process_email(message: types.Message, state: FSMContext):
    email_raw = message.text.strip()

    #1 List of phrases we consider "skip"
    skip_options = ["-", "пропустить", "нет", "не нужно", "skip", "none", "обойдусь"]

    #2. Email Verification Logic
    if email_raw.lower() in skip_options:
        email = None
        email_text = "не указан (копии на почту не будут приходить)"
    else:
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if not re.match(email_pattern, email_raw):
            await message.answer(
                "⚠️ **Ошибка в формате email.**\n\n"
                "Пожалуйста, введите корректный адрес (например: example@mail.ru) "
                "или напишите слово «пропустить»:"
            )
            return  # Прерываем выполнение, ждем новый ввод

        email = email_raw
        email_text = email

    #3. Extracting accumulated data from FSM
    user_data = await state.get_data()
    organization = user_data.get('organization')
    inn = user_data.get('inn')

    #4. Saving to Django Database via sync_to_async
    try:
        client, created = await sync_to_async(Client.objects.update_or_create)(
            inn=inn,
            defaults={
                'name': organization,
                'email': email,
                'telegram_chat_id': str(message.chat.id),
            }
        )

        status_text = "успешно зарегистрирован" if created else "ваши данные обновлены"

        # 5. Final response to the user
        response = (
            f"Готово! 🎉\n\n"
            f"Вы {status_text}:\n"
            f"🏢 **Организация:** {organization}\n"
            f"🆔 **ИНН/ОГРН:** {inn}\n"
            f"📧 **Email:** {email_text}\n\n"
            f"Теперь счета будут приходить сюда автоматически. ✅\n"
            f"Ваш ID в системе: `{client.id}`"
        )

        # Remove the keyboard (Registration button), as it is no longer needed
        await message.answer(response, reply_markup=types.ReplyKeyboardRemove())
        await state.clear()  # Очищаем состояние после успешного завершения

    except Exception as e:
        logging.error(f"Ошибка при сохранении клиента: {e}")
        await message.answer("❌ Произошла ошибка при сохранении данных. Попробуйте позже или обратитесь в поддержку.")


from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота и получить справку"),
        BotCommand(command="registration", description="Зарегистрироваться или обновить данные"),
    ]

    # Set up commands for all users
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main():
    # Customizing the command menu
    await set_commands(bot)

    # Launch the bot
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
