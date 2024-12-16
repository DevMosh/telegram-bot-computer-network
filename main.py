import re
import sqlite3

import paramiko
from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from database import create_connection, create_tables, add_email, add_phone_number, get_all_emails, \
    get_all_phone_numbers

router = Router()


class Search(StatesGroup):
    number = State()
    email = State()
    email_add = State()
    number_add = State()


# Создание соединения и таблиц
conn = create_connection()
create_tables(conn)


@router.message(CommandStart(), StateFilter("*"))
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Добро пожаловать в бот!\n\n"
                         "Доступные команды:\n"
                         "/find_email - поиск почты\n"
                         "/find_phone_number - поиск номера\n\n"
                         "/add_email - добавить почту\n"
                         "/add_phone_number - добавить номер")


@router.message(F.text, Command('find_email'))
async def find_email(message: Message, state: FSMContext) -> None:
    await message.answer("Отправьте ваш email: ")
    await state.set_state(Search.email)


@router.message(Search.email)
async def find_email_state(message: Message, state: FSMContext):
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    def is_valid_email(email):
        return re.match(email_pattern, email) is not None

    emails = get_all_emails(conn)
    if message.text in emails:
        await message.answer("Почта найдена.")
    elif not is_valid_email(message.text):
        await message.answer('Не правильный формат почты.')
    else:
        await message.answer("Почта не найдена, введите корректную почту или отмените действие отправив /start.")
        await state.set_state(Search.email)


@router.message(F.text, Command('add_email'))
async def add_email_command(message: Message, state: FSMContext) -> None:
    await message.answer("Отправьте email для добавления: ")
    await state.set_state(Search.email_add)


@router.message(Search.email_add)
async def add_email_state(message: Message, state: FSMContext):
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if re.match(email_pattern, message.text):
        try:
            add_email(conn, message.text)
            await message.answer("Почта добавлена в базу данных.")
        except sqlite3.IntegrityError:
            await message.answer("Эта почта уже существует в базе данных.")
    else:
        await message.answer('Не правильный формат почты.')


@router.message(F.text, Command('find_phone_number'))
async def find_phone_number(message: Message, state: FSMContext) -> None:
    await message.answer("Отправьте ваш номер телефона: ")
    await state.set_state(Search.number_add)


@router.message(Search.number_add)
async def find_phone_state(message: Message, state: FSMContext):
    phone_pattern = r"^(\+7|8)[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}$"

    def is_valid_phone(phone):
        return re.match(phone_pattern, phone) is not None

    if is_valid_phone(message.text):
        phone_number = message.text
        normalized_phone = re.sub(r"[^\d+]", "", phone_number)
        if normalized_phone.startswith("8"):
            normalized_phone = "+7" + normalized_phone[1:]

        phone_numbers = get_all_phone_numbers(conn)
        if normalized_phone in phone_numbers:
            await message.answer("Номер найден.")
        else:
            await message.answer("Номер не найден, введите корректный номер или отмените действие отправив /start.")
    else:
        await message.answer("Не правильный формат ввода номера.")


@router.message(F.text, Command('add_phone_number'))
async def add_phone_number_command(message: Message, state: FSMContext) -> None:
    await message.answer("Отправьте номер телефона для добавления: ")
    await state.set_state(Search.number)


@router.message(Search.number)
async def add_phone_state(message: Message, state: FSMContext):
    phone_pattern = r"^(\+7|8)[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}$"

    if re.match(phone_pattern, message.text):
        try:
            add_phone_number(conn, message.text)
            await message.answer("Номер добавлен в базу данных.")
        except sqlite3.IntegrityError:
            await message.answer("Этот номер уже существует в базе данных.")
    else:
        await message.answer("Не правильный формат ввода номера.")


@router.message(F.text, Command('linux'))
async def linux_command(message: Message) -> None:
    ip_address = '89.110.116.180'
    username = 'root'
    password = '9u2r6AiNiHfyF83F'

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip_address, username=username, password=password)

        commands = [
            'uname -a',
            'lsb_release -a',
            'speedtest-cli --simple'
        ]

        output = ""
        for command in commands:
            stdin, stdout, stderr = client.exec_command(command)
            command_output = stdout.read().decode()
            command_error = stderr.read().decode()

            output += f"Команда: {command}\n"
            output += command_output + "\n"
            if command_error:
                output += f"Ошибка:\n{command_error}\n"

        # Закрытие подключения
        client.close()

        await message.answer(f"Результаты:\n{output}")

    except Exception as e:
        await message.answer(f"Произошла ошибка при подключении к серверу: {e}")


@router.message()
async def other_message(message: Message):
    await message.answer('Такой команды не существует! Отправьте /start, чтобы узнать существующие команды.')
