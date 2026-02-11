import os
import django
import asyncio
import logging
import sys
import re
from typing import Optional, List, Dict, Any, Tuple, Final

# ────────────────────────────────────────────────
# Initializing Django
# ────────────────────────────────────────────────

# Calculate the project root path
BASE_DIR: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Append project root to sys.path for module resolution
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Configure Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

# Initialize Django ORM and applications
django.setup()

from clients.models import Client
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from asgiref.sync import sync_to_async
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import BotCommand, BotCommandScopeDefault

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize Bot and Dispatcher with memory storage
bot: Bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=MemoryStorage())


class RegisterForm(StatesGroup):
    """
        Finite State Machine (FSM) states for the client registration process.

        Attributes:
            organization: State for capturing the legal entity or person name.
            inn: State for capturing the tax identification number (INN/OGRN).
            email: State for capturing the contact email for invoice copies.
    """
    organization: State = State()
    inn: State = State()
    email: State = State()


@dp.message(F.text == "📝 Регистрация")
async def btn_registration(message: types.Message, state: FSMContext) -> None:
    """
        Entry point for registration triggered by the reply keyboard button.

        Args:
            message: The incoming message from the user.
            state: The FSM context for managing user registration flow.
    """
    await cmd_registration(message, state)


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    """
        Handles the /start command.

        Provides a welcome message and initializes the main interaction menu.
    """
    builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    builder.button(text="📝 Регистрация")
    builder.adjust(1)

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
async def cmd_registration(message: types.Message, state: FSMContext) -> None:
    """
        Processes the organization name and transitions to the INN input state.
    """
    await message.answer(
        "Отлично, начинаем регистрацию! 📝\n\n"
        "Напиши название организации (или ФИО, если ИП):"
    )
    await state.set_state(RegisterForm.organization)


@dp.message(RegisterForm.organization)
async def process_organization(message: types.Message, state: FSMContext) -> None:
    """
        Processes the organization name and transitions to the INN input state.
    """
    raw_text: Optional[str] = message.text
    if not raw_text:
        return

    text: str = raw_text.strip()
    if not text:
        await message.answer("Название организации не может быть пустым. Попробуй ещё раз:")
        return

    await state.update_data(organization=text)
    await message.answer("Отлично! Теперь ИНН или ОГРН:")
    await state.set_state(RegisterForm.inn)


@dp.message(RegisterForm.inn)
async def process_inn(message: types.Message, state: FSMContext) -> None:
    """
            Validates the INN/OGRN format and transitions to the email input state.

            Validation:
                - Must be numeric.
                - Must be 10 or 12 characters long.
    """
    raw_inn: Optional[str] = message.text
    if not raw_inn:
        return

    inn: str = raw_inn.strip()

    # Validate that INN contains only digits and has a proper length
    if not inn.isdigit() or len(inn) not in [10, 12]:
        await message.answer(
            "⚠️ Некорректный ИНН.\n"
            "ИНН должен состоять только из цифр и иметь длину 10 или 12 символов.\n"
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
async def process_email(message: types.Message, state: FSMContext) -> None:
    """
        Finalizes registration, validates email (or skip), and saves data to Django DB.

        Note:
            Uses `sync_to_async` for non-blocking database operations via Django ORM.
    """
    raw_input: Optional[str] = message.text
    if not raw_input:
        return

    email_raw: str = raw_input.strip()
    skip_options: List[str] = ["-", "пропустить", "нет", "не нужно", "skip", "none", "обойдусь"]

    email: Optional[str] = None
    email_text: str = "не указан (копии на почту не будут приходить)"

    # Check if the user chose to skip email registration
    if email_raw.lower() not in skip_options:
        email_pattern: str = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if not re.match(email_pattern, email_raw):
            await message.answer(
                "⚠️ **Ошибка в формате email.**\n\n"
                "Пожалуйста, введите корректный адрес или напишите слово «пропустить»:"
            )
            return

        email = email_raw
        email_text = email

    # Retrieve accumulated data from FSM storage
    user_data: Dict[str, Any] = await state.get_data()
    organization: str = user_data.get('organization', 'Unknown')
    inn: str = user_data.get('inn', '')

    try:
        # Save or update client data in the Django database
        db_result: Tuple[Client, bool] = await sync_to_async(Client.objects.update_or_create)(
            inn=inn,
            defaults={
                'name': organization,
                'email': email,
                'telegram_chat_id': str(message.chat.id),
            }
        )
        client, created = db_result

        status_text: str = "успешно зарегистрирован" if created else "ваши данные обновлены"

        response: str = (
            f"Готово! 🎉\n\n"
            f"Вы {status_text}:\n"
            f"🏢 **Организация:** {organization}\n"
            f"🆔 **ИНН/ОГРН:** {inn}\n"
            f"📧 **Email:** {email_text}\n\n"
            f"Теперь счета будут приходить сюда автоматически. ✅\n"
            f"Ваш ID в системе: `{client.id}`"
        )

        await message.answer(response, reply_markup=types.ReplyKeyboardRemove())
        await state.clear()

    except Exception as e:
        logging.error(f"Error saving client to database: {e}")
        await message.answer("❌ Произошла ошибка при сохранении данных.")


async def set_commands(bot: Bot) -> None:
    """Configures the bot's command menu in the Telegram interface."""
    commands: List[BotCommand] = [
        BotCommand(command="start", description="Запустить бота и получить справку"),
        BotCommand(command="registration", description="Зарегистрироваться или обновить данные"),
    ]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def main() -> None:
    """
    Main entry point for the bot service.

    Initializes commands and starts long-polling.
    """
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot execution interrupted by user")
