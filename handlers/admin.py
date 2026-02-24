from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database import async_session_maker
from models import Request, User
from services import xui_api, utils
import config
import asyncio
import subprocess

router = Router()

@router.callback_query(F.data.startswith("approve_"))
async def approve_request(callback: CallbackQuery):
    req_id = int(callback.data.split("_")[1])
    
    async with async_session_maker() as session:
        # 1. Получаем заявку
        result = await session.execute(select(Request).where(Request.id == req_id))
        req = result.scalar_one_or_none()

        if not req or req.status != "pending":
            await callback.answer("Заявка уже обработана или не найдена.")
            return

        # 2. Получаем пользователя
        user_result = await session.execute(select(User).where(User.id == req.user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            await callback.answer("Пользователь не найден.")
            return

        # 3. Создаем логин - в xui это email
        if user.username:
            clean_username = user.username.lstrip('@')
            email = f"{clean_username}@from_bot"
        else:
            email = f"tg_{user.telegram_id}@from_bot"

        try:
            # 4. Создаем пользователя в xui
            uuid = await xui_api.create_user_in_xui(email)

            # 5. Обновляем статус заявки
            req.status = "active"
            req.uuid = uuid
            await session.commit()

            # 6. Генерируем ссылку
            link = utils.generate_vless_link(uuid, f"VLESS-{user.telegram_id}")

            # 7. Отправляем пользователю
            await callback.bot.send_message(
                user.telegram_id,
                f"🎉 <b>Ваша заявка одобрена!</b>\n\n"
                "Ваш аккаунт создан и будет активирован в течение 2 минут. Вот ваша ссылка:\n\n"
                f"<code>{link}</code>",
                parse_mode="HTML"
            )

            panel_link = f'<a href="{config.XUI_BASE_URL}/panel/inbounds">Панель X-UI</a>'

            # 8. Сообщаем админу
            await callback.message.edit_text(
                f"✅ Заявка #{req_id} одобрена.\n"
                f"Пользователь: @{user.username or user.telegram_id}\n"
                f"Email: {email}\n"
                f"UUID: {uuid}\n\n"
                f"⚠️ <b>Важно:</b> Зайдите в {panel_link} и нажмите 'Сохранить' на Inbound, чтобы активировать подключение.",
                parse_mode="HTML"
            )
            await callback.answer("Одобрено")

        except Exception as e:
            await callback.answer(f"Ошибка: {e}")
            print(f"Error: {e}")

@router.callback_query(F.data.startswith("reject_"))
async def reject_request(callback: CallbackQuery):
    req_id = int(callback.data.split("_")[1])
    
    async with async_session_maker() as session:
        await session.execute(update(Request).where(Request.id == req_id).values(status="rejected"))
        await session.commit()

        await callback.message.edit_text(f"❌ Заявка #{req_id} отклонена.")
        await callback.answer("Отклонено")

@router.callback_query(F.data == "cancel_create")
async def cancel_create(callback: CallbackQuery):
    await callback.message.edit_text("❌ Вы отменили создание заявки.")
    await callback.answer("Отменено")

# --- НОВЫЕ ФУНКЦИИ ДЛЯ ПЕРЕЗАГРУЗКИ ---

@router.message(Command("reset_xray"))
async def cmd_reset_xray(message: Message):
    """
    Команда для админа: Показывает кнопку для ручной перезагрузки Xray.
    """
    if message.from_user.id not in config.ADMINS_ID:
        await message.answer("⛔ Эта команда только для администраторов.")
        return

    # Формируем клавиатуру
    kb = InlineKeyboardBuilder()
    kb.button(text="⚠️ ПЕРЕЗАГРУЗИТЬ XRAY", callback_data="exec_reset_xray")
    kb.button(text="Отмена", callback_data="cancel_reset")
    
    await message.answer(
        "Вы уверены, что хотите перезагрузить ядро Xray?\n\n"
        "Это прервет текущие соединения на пару секунд.",
        reply_markup=kb.as_markup()
    )

@router.callback_query(F.data == "exec_reset_xray")
async def exec_reset_xray(callback: CallbackQuery):
    """
    Обработка нажатия кнопки. Выполняет systemctl restart x-ui.
    """
    # Ответ пользователю, чтобы не висело "часики"
    await callback.answer("⏳ Перезагружаю Xray...", show_alert=False)

    try:
        print("[DEBUG] Перезагрузка Xray через команду админа...")
        
        # Запускаем процесс в асинхронном режиме, чтобы не блокировать бота
        proc = await asyncio.create_subprocess_exec(
            "systemctl",
            "restart",
            "x-ui",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            # Уведомляем админа об успехе
            try:
                await callback.message.edit_text(
                    f"✅ Xray успешно перезагружен!\n\n"
                    f"Статус: Активен.\n"
                    f"Настройки применены."
                )
            except Exception:
                # Если сообщение уже нельзя редактировать, шлем новое
                await callback.bot.send_message(
                    callback.message.chat.id,
                    "✅ Xray успешно перезагружен!"
                )
        else:
            await callback.message.edit_text(
                f"❌ Ошибка перезагрузки!\n\n"
                f"Код: {proc.returncode}\n"
                f"Ошибка: {stderr.decode()}"
            )

    except Exception as e:
        await callback.answer("Ошибка при выполнении команды")
        await callback.message.reply_text(f"⚠️ Не удалось выполнить команду: {e}")

@router.callback_query(F.data == "cancel_reset")
async def cancel_reset(callback: CallbackQuery):
    await callback.message.edit_text("❌ Операция отменена.")
    await callback.answer("Отменено")
