from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, создать", callback_data="confirm_create")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_create")]
        ]
    )

def get_admin_moderation_kb(request_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{request_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{request_id}")
            ]
        ]
    )
