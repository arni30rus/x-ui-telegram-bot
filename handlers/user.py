from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database import async_session_maker
from models import Request, User
from services import xui_api, utils
import keyboards
import config

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    async with async_session_maker() as session:
        # Ищем пользователя
        result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalar_one_or_none()
        
        if not user:
            # Создаем пользователя
            user = User(telegram_id=message.from_user.id, username=message.from_user.username)
            session.add(user)
            await session.commit()
        
        await message.answer(
            f"Привет, {message.from_user.first_name}!\n"
            "Я бот для управления VLESS доступом.\n"
            "Команды:\n"
            "/request_account - Запросить доступ\n"
            "/my_account - Моя конфигурация"
        )

@router.message(Command("request_account"))
async def cmd_request(message: Message):
    async with async_session_maker() as session:
        # 1. Ищем пользователя
        result = await session.execute(select(User).where(User.telegram_id == message.from_user.id))
        user = result.scalar_one_or_none()

        # 2. Если пользователя нет — создаем
        if not user:
            user = User(telegram_id=message.from_user.id, username=message.from_user.username)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        # 3. Проверяем наличие активной заявки
        result = await session.execute(
            select(Request).where(Request.user_id == user.id, Request.status == "active")
        )
        req = result.scalar_one_or_none()
        
        if req:
            await message.answer("У вас уже есть активный аккаунт.")
            return

        # 4. Создаем новую заявку
        new_req = Request(user_id=user.id, status="pending")
        session.add(new_req)
        await session.commit()
        
        await message.answer(
            "Вы хотите запросить новый VLESS аккаунт?", 
            reply_markup=keyboards.get_confirm_keyboard()
        )

@router.callback_query(F.data == "confirm_create")
async def confirm_request(callback: CallbackQuery):
    """
    Обработка нажатия кнопки "Да, создать".
    """
    user_id = callback.from_user.id
    
    async with async_session_maker() as session:
        # 1. Находим или создаем пользователя
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(telegram_id=user_id, username=callback.from_user.username)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
        # 2. Проверяем, нет ли уже активной заявки
        result = await session.execute(
            select(Request).where(Request.user_id == user.id, Request.status == "active")
        )
        if result.scalar_one_or_none():
            await callback.answer("У вас уже есть активный аккаунт.")
            return

        # 3. Создаем заявку
        new_req = Request(user_id=user.id, status="pending")
        session.add(new_req)
        await session.commit()
        await session.refresh(new_req)

        # 4. Уведомляем админов
        text = (
            f"🆕 <b>Новая заявка!</b>\n"
            f"👤 Пользователь: @{user.username or 'скрыт'} (ID: {user.telegram_id})\n"
            f"📅 Время: {new_req.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"🆔 ID заявки: {new_req.id}"
        )
        
        for admin_id in config.ADMINS_ID:
            try:
                await callback.bot.send_message(
                    admin_id, 
                    text, 
                    parse_mode="HTML",
                    reply_markup=keyboards.get_admin_moderation_kb(new_req.id)
                )
            except Exception as e:
                print(f"Не удалось уведомить админа {admin_id}: {e}")

        await callback.message.edit_text("✅ Заявка отправлена на модерацию.")
        await callback.answer("Успешно")

@router.callback_query(F.data == "cancel_create")
async def cancel_create(callback: CallbackQuery):
    """
    Обработка нажатия кнопки "Отмена".
    """
    await callback.message.edit_text("❌ Вы отменили создание заявки.")
    await callback.answer("Отменено")

@router.message(Command("my_account"))
async def cmd_my_account(message: Message):
    async with async_session_maker() as session:
        result = await session.execute(
            select(Request).join(User).where(
                User.telegram_id == message.from_user.id, 
                Request.status == "active"
            )
        )
        req = result.scalar_one_or_none()
        
        if not req:
            await message.answer("У вас нет активного аккаунта.")
            return

        link = utils.generate_vless_link(req.uuid, f"VLESS-{req.user_id}")
        
        await message.answer(
            f"🔑 <b>Ваша конфигурация:</b>\n\n"
            f"<code>{link}</code>",
            parse_mode="HTML"
        )
